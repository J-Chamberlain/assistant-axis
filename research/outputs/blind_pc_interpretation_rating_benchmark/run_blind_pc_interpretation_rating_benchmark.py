#!/usr/bin/env python3
"""Coordinate-blind GPT-5.5 PC-interpretation rating benchmark.

This script uses Codex CLI `gpt-5.5` as a deterministic blinded rater. The
rater prompt contains role instructions only; it does not include PC/PCA labels,
coordinates, rankings, clusters, assistant-axis values, or benchmark targets.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler


REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "research" / "outputs" / "blind_pc_interpretation_rating_benchmark"
RAW_DIR = OUT / "raw_codex_batches"
SHARED = REPO / "research" / "q2_stability" / "qwen" / "outputs" / "shared_latent_feature_benchmark"
INSTRUCTION_DIR = REPO / "data" / "roles" / "instructions"

RATER_MODEL = "gpt-5.5"
MODEL_USED = "GPT-5.5"

PRIOR_BENCHMARKS = [
    ("semantic_baseline", 0.516873, 0.180967, 0.335665, 0.389397),
    ("codex_trait_replication", math.nan, math.nan, math.nan, 0.398000),
    ("codex_retained_procedural_behavioral", 0.631205, 0.257221, 0.422097, 0.490090),
    ("claude_bigfive", 0.733515, 0.480321, 0.415511, 0.612979),
    ("hierarchical_model", math.nan, math.nan, math.nan, 0.622000),
    ("residual_manifold", math.nan, math.nan, math.nan, 0.632000),
    ("semantic_bigfive_svd15", math.nan, math.nan, math.nan, 0.707000),
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_instructions(role: str) -> list[str]:
    data = load_json(INSTRUCTION_DIR / f"{role}.json")
    return [item["pos"] for item in data.get("instruction", []) if isinstance(item, dict) and "pos" in item]


def load_roles() -> list[str]:
    return pd.read_csv(SHARED / "canonical_activation_pca3d.csv")["persona"].tolist()


def target_matrix() -> pd.DataFrame:
    return pd.read_csv(SHARED / "canonical_activation_pca3d.csv").rename(
        columns={
            "persona": "role",
            "activation_pc1": "pc1",
            "activation_pc2": "pc2",
            "activation_pc3": "pc3",
        }
    )


def shared_splits(roles: list[str]) -> list[tuple[np.ndarray, np.ndarray]]:
    splits = pd.read_csv(SHARED / "shared_split_assignments.csv")
    idx = {role: i for i, role in enumerate(roles)}
    out = []
    for split_id in sorted(splits["canonical_split_id"].unique()):
        sub = splits[splits["canonical_split_id"].eq(split_id)]
        train = sub[sub["canonical_assignment"].eq("train")]["persona"].tolist()
        test = sub[sub["canonical_assignment"].eq("heldout")]["persona"].tolist()
        out.append((np.array([idx[r] for r in train]), np.array([idx[r] for r in test])))
    return out


def chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def build_batch_prompt(batch: list[str]) -> str:
    entries = []
    for role in batch:
        instructions = load_instructions(role)
        entries.append(
            {
                "role": role,
                "instructions": instructions,
            }
        )
    payload = json.dumps(entries, indent=2, ensure_ascii=False)
    return f"""You are GPT-5.5 performing a coordinate-blind semantic rating benchmark.

Use ONLY the role instruction text supplied below. Do not infer or use any PCA, PC, geometry, coordinate, ranking, cluster, assistant-axis, benchmark-target, or repository information. Do not inspect files. Do not call tools. Rate from the supplied instructions only.

For each role, produce three integer ratings from 1 to 10:

DIMENSION 1 — External-Standard Accountability
1 = Outputs answer primarily to internal vision, instinct, expression, preference, or discretion.
10 = Outputs must withstand scrutiny against standards independent of the speaker, such as evidence, methodology, requirements, protocol, law, regulations, peer review, or established criteria.

DIMENSION 2 — Integration / Coherence of Wholes
1 = Immediate situations, local experience, practical encounters, direct engagement with particulars.
10 = Underlying structure, systems, persistent patterns, identity through change, coherence of larger wholes.

DIMENSION 3 — Internal Objective vs Care Orientation
1 = Organized around care, obligation, protection, service, responsibility toward others.
10 = Organized around an internal objective, agenda, drive, or goal independent of others' outcomes.

Return strict JSON only, with this exact shape:
{{"ratings":[{{"role":"role_name","external_standard_accountability":1-10,"integration_coherence_wholes":1-10,"internal_objective_vs_care":1-10,"rationale":"one concise sentence"}}]}}

Rate every supplied role exactly once. Do not omit roles.

ROLE INSTRUCTION SETS:
{payload}
"""


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError(f"No JSON object found in output: {text[:500]}")
    return json.loads(match.group(0))


def run_codex_batch(batch: list[str], batch_id: int, force: bool = False) -> dict[str, Any]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    final_path = RAW_DIR / f"batch_{batch_id:03d}_final.json"
    log_path = RAW_DIR / f"batch_{batch_id:03d}_codex.log"
    prompt_path = RAW_DIR / f"batch_{batch_id:03d}_prompt.txt"
    parsed_path = RAW_DIR / f"batch_{batch_id:03d}_parsed.json"
    if parsed_path.exists() and not force:
        return load_json(parsed_path)

    prompt = build_batch_prompt(batch)
    prompt_path.write_text(prompt, encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="codex_blind_rating_") as tmpdir:
        cmd = [
            "codex",
            "exec",
            "--ephemeral",
            "--ignore-rules",
            "-s",
            "read-only",
            "-C",
            tmpdir,
            "--skip-git-repo-check",
            "-m",
            RATER_MODEL,
            "-o",
            str(final_path),
            "-",
        ]
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=240,
        )
    log_path.write_text(proc.stdout, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"Codex batch {batch_id} failed with code {proc.returncode}: {proc.stdout[-2000:]}")
    parsed = extract_json(final_path.read_text(encoding="utf-8"))
    parsed["batch_id"] = batch_id
    parsed["expected_roles"] = batch
    parsed_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
    return parsed


def collect_ratings(batch_size: int, force: bool) -> pd.DataFrame:
    roles = load_roles()
    records = []
    for batch_id, batch in enumerate(chunks(roles, batch_size), start=1):
        print(f"rating batch {batch_id}/{math.ceil(len(roles)/batch_size)} ({len(batch)} roles)")
        parsed = run_codex_batch(batch, batch_id, force=force)
        got = parsed.get("ratings", [])
        got_roles = {item.get("role") for item in got}
        missing = [role for role in batch if role not in got_roles]
        if missing:
            raise RuntimeError(f"Batch {batch_id} missing roles: {missing}")
        for item in got:
            role = item["role"]
            if role not in batch:
                raise RuntimeError(f"Batch {batch_id} returned unexpected role {role}")
            rec = {
                "role": role,
                "external_standard_accountability": int(item["external_standard_accountability"]),
                "integration_coherence_wholes_raw": int(item["integration_coherence_wholes"]),
                "integration_coherence_wholes_signed_for_pc2": -int(item["integration_coherence_wholes"]),
                "internal_objective_vs_care": int(item["internal_objective_vs_care"]),
                "rationale": str(item.get("rationale", "")),
                "rating_model": RATER_MODEL,
                "batch_id": batch_id,
            }
            for col in [
                "external_standard_accountability",
                "integration_coherence_wholes_raw",
                "internal_objective_vs_care",
            ]:
                if rec[col] < 1 or rec[col] > 10:
                    raise RuntimeError(f"Invalid rating {col}={rec[col]} for role {role}")
            records.append(rec)
        time.sleep(1)
    ratings = pd.DataFrame(records)
    # Preserve canonical row order.
    order = {role: i for i, role in enumerate(roles)}
    ratings["order"] = ratings["role"].map(order)
    return ratings.sort_values("order").drop(columns=["order"])


def heldout_axis_r2(x: np.ndarray, y: np.ndarray, splits: list[tuple[np.ndarray, np.ndarray]]) -> tuple[float, list[float]]:
    vals = []
    for train_idx, test_idx in splits:
        scaler = StandardScaler()
        xt = scaler.fit_transform(x[train_idx])
        xv = scaler.transform(x[test_idx])
        model = Ridge(alpha=1.0)
        model.fit(xt, y[train_idx])
        pred = model.predict(xv)
        vals.append(float(r2_score(y[test_idx], pred)))
    return float(np.mean(vals)), vals


def evaluate_models(ratings: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    targets = target_matrix()
    joined = targets.merge(ratings, on="role", how="inner")
    roles = targets["role"].tolist()
    if len(joined) != len(roles):
        raise RuntimeError(f"Rating join produced {len(joined)} rows, expected {len(roles)}")
    splits = shared_splits(roles)
    y = joined[["pc1", "pc2", "pc3"]].to_numpy(float)

    models = {
        "A_pc1_from_external_standard_only": {
            "features": ["external_standard_accountability"],
            "axes": [0],
        },
        "B_pc2_from_integration_only_signed": {
            "features": ["integration_coherence_wholes_signed_for_pc2"],
            "axes": [1],
        },
        "C_pc3_from_internal_objective_only": {
            "features": ["internal_objective_vs_care"],
            "axes": [2],
        },
        "D_joint_three_dimension_model": {
            "features": [
                "external_standard_accountability",
                "integration_coherence_wholes_signed_for_pc2",
                "internal_objective_vs_care",
            ],
            "axes": [0, 1, 2],
        },
    }

    rows = []
    details: dict[str, Any] = {}
    for name, spec in models.items():
        x = joined[spec["features"]].to_numpy(float)
        axis_r2 = [math.nan, math.nan, math.nan]
        split_values: dict[str, list[float]] = {}
        for axis in spec["axes"]:
            mean, vals = heldout_axis_r2(x, y[:, axis], splits)
            axis_r2[axis] = mean
            split_values[f"pc{axis+1}"] = vals
        mean_r2 = float(np.nanmean(axis_r2))
        rows.append(
            {
                "feature_family": name,
                "pc1_r2": axis_r2[0],
                "pc2_r2": axis_r2[1],
                "pc3_r2": axis_r2[2],
                "mean_r2": mean_r2,
                "n_features": len(spec["features"]),
                "n_personas": len(joined),
                "source": "this_run_blind_gpt55_ratings",
            }
        )
        details[name] = {"features": spec["features"], "split_r2": split_values}
    return pd.DataFrame(rows), details


def write_rankings(ratings: pd.DataFrame) -> None:
    mapping = {
        "pc1_rating_rankings.csv": "external_standard_accountability",
        "pc2_rating_rankings.csv": "integration_coherence_wholes_raw",
        "pc3_rating_rankings.csv": "internal_objective_vs_care",
    }
    for filename, col in mapping.items():
        out = ratings[["role", col, "rationale"]].sort_values([col, "role"], ascending=[False, True])
        out.to_csv(OUT / filename, index=False)


def write_outputs(ratings: pd.DataFrame, model_results: pd.DataFrame, details: dict[str, Any]) -> None:
    ratings.to_csv(OUT / "role_dimension_ratings.csv", index=False)
    write_rankings(ratings)

    prior_rows = [
        {
            "feature_family": name,
            "pc1_r2": pc1,
            "pc2_r2": pc2,
            "pc3_r2": pc3,
            "mean_r2": mean,
            "n_features": math.nan,
            "n_personas": 273,
            "source": "prior_shared_benchmark",
        }
        for name, pc1, pc2, pc3, mean in PRIOR_BENCHMARKS
    ]
    comparison = pd.concat([pd.DataFrame(prior_rows), model_results], ignore_index=True)
    comparison.to_csv(OUT / "benchmark_comparison.csv", index=False)

    payload = {
        "status": "complete",
        "rating_model": RATER_MODEL,
        "model_used": MODEL_USED,
        "n_roles": int(len(ratings)),
        "blindness": {
            "rater_saw": "role instructions only",
            "rater_did_not_see": [
                "PC coordinates",
                "PCA labels",
                "rankings",
                "cluster assignments",
                "assistant-axis values",
                "geometry information",
                "benchmark targets",
            ],
        },
        "model_results": model_results.to_dict(orient="records"),
        "split_details": details,
        "ratings": ratings.to_dict(orient="records"),
    }
    (OUT / "blind_rating_results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    joint = model_results[model_results["feature_family"].eq("D_joint_three_dimension_model")].iloc[0]
    sem = 0.389397
    codex = 0.490090
    big5 = 0.612979
    svd = 0.707000
    top_pc1 = ratings.sort_values(["external_standard_accountability", "role"], ascending=[False, True]).head(15)
    low_pc1 = ratings.sort_values(["external_standard_accountability", "role"], ascending=[True, True]).head(15)
    top_pc2 = ratings.sort_values(["integration_coherence_wholes_raw", "role"], ascending=[False, True]).head(15)
    low_pc2 = ratings.sort_values(["integration_coherence_wholes_raw", "role"], ascending=[True, True]).head(15)
    top_pc3 = ratings.sort_values(["internal_objective_vs_care", "role"], ascending=[False, True]).head(15)
    low_pc3 = ratings.sort_values(["internal_objective_vs_care", "role"], ascending=[True, True]).head(15)

    def role_list(df: pd.DataFrame, col: str) -> str:
        return ", ".join(f"{r.role} ({getattr(r, col)})" for r in df.itertuples(index=False))

    report = f"""# Blind PC Interpretation Rating Benchmark

`model_used`: GPT-5.5. Rater model: `{RATER_MODEL}` through Codex CLI.

## Startup Status

Startup check passed. Raw GitHub startup files were fetched with cache-busting and verified against `research/STARTUP_MANIFEST.md` before analysis.

## Method

The benchmark used the same 273-persona canonical Qwen activation PCA3D rows and deterministic split assignments as `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`. The rater saw only the five role instructions for each role. It did not see PC coordinates, PCA labels, rankings, cluster assignments, assistant-axis values, geometry information, or benchmark targets.

Ratings were deterministic at the task level: Codex CLI was invoked with `-m gpt-5.5`, read-only sandboxing, a temporary non-repo working directory, and strict JSON output. Role ratings are stored in `role_dimension_ratings.csv`; raw batch prompts/finals/logs are stored under `raw_codex_batches/`.

Dimension signs:

- PC1: higher External-Standard Accountability -> higher PC1.
- PC2: higher Integration / Coherence of Wholes -> more negative PC2. The CSV stores both raw integration score and signed `-integration` value used for prediction.
- PC3: higher Internal Objective vs Care Orientation -> higher PC3.

## Results

| Model | PC1 R2 | PC2 R2 | PC3 R2 | Mean R2 |
|---|---:|---:|---:|---:|
"""
    for row in model_results.itertuples(index=False):
        def fmt(x: float) -> str:
            return "" if pd.isna(x) else f"{x:.3f}"
        report += f"| {row.feature_family} | {fmt(row.pc1_r2)} | {fmt(row.pc2_r2)} | {fmt(row.pc3_r2)} | {row.mean_r2:.3f} |\n"

    report += f"""
## Comparison To Prior Benchmarks

| Feature family | Mean R2 |
|---|---:|
| Semantic baseline | {sem:.3f} |
| Codex trait replication | 0.398 |
| Codex procedural features | {codex:.3f} |
| Claude Big Five | {big5:.3f} |
| Hierarchical model | 0.622 |
| Residual manifold | 0.632 |
| Semantic + Big Five + SVD15 | {svd:.3f} |
| GPT-5.5 blind three-rating joint model | {joint.mean_r2:.3f} |

## Observed

- Rated roles: {len(ratings)}.
- Joint three-dimension model: PC1 R2={joint.pc1_r2:.3f}, PC2 R2={joint.pc2_r2:.3f}, PC3 R2={joint.pc3_r2:.3f}, mean R2={joint.mean_r2:.3f}.
- The three blind ratings are {'stronger than' if joint.mean_r2 > sem else 'weaker than'} the semantic baseline mean R2 ({joint.mean_r2:.3f} vs {sem:.3f}).
- The three blind ratings are {'stronger than' if joint.mean_r2 > codex else 'weaker than'} the Codex procedural feature mean R2 ({joint.mean_r2:.3f} vs {codex:.3f}).
- The three blind ratings are {'competitive with' if abs(joint.mean_r2 - big5) < 0.05 else ('stronger than' if joint.mean_r2 > big5 else 'weaker than')} Claude Big Five mean R2 ({joint.mean_r2:.3f} vs {big5:.3f}).

## Dimension Extremes

### External-Standard Accountability

Highest 15: {role_list(top_pc1, 'external_standard_accountability')}

Lowest 15: {role_list(low_pc1, 'external_standard_accountability')}

### Integration / Coherence of Wholes

Highest 15: {role_list(top_pc2, 'integration_coherence_wholes_raw')}

Lowest 15: {role_list(low_pc2, 'integration_coherence_wholes_raw')}

### Internal Objective vs Care Orientation

Highest 15: {role_list(top_pc3, 'internal_objective_vs_care')}

Lowest 15: {role_list(low_pc3, 'internal_objective_vs_care')}

## Inferred

If the joint model exceeds or approaches the compact-feature benchmarks, that supports the current three-axis interpretation as semantically recoverable from role instructions alone. If it falls below the semantic baseline or only predicts one axis, the interpretation should remain provisional and axis-specific.

## Speculative

Large differences between axis-specific and joint scores may indicate that the current labels capture one or two strong axes while missing residual structure, or that role instructions encode axes unevenly. Follow-up should inspect roles with high rating/coordinate disagreement rather than treating the benchmark as final.

## Caveats

- This benchmark tests whether the current interpretations predict released activation geometry from blinded role instructions. It does not establish causal semantics or execution-time response behavior.
- The rater is GPT-5.5 via Codex CLI, not a human panel.
- The role instructions themselves contain role labels, because they are the original role-conditioning artifacts; the rater was blind to geometry, not blind to role wording.
- Do not describe these results as confirmed, proven, or solved.
"""
    (OUT / "blind_pc_interpretation_rating_report.md").write_text(report, encoding="utf-8")

    inventory = pd.DataFrame(
        [
            {
                "artifact": p.name,
                "path": str(p.relative_to(REPO)),
                "status": "active",
                "description": "Blind PC interpretation rating benchmark artifact.",
            }
            for p in sorted(OUT.iterdir())
            if p.name != "artifact_inventory.csv"
        ]
    )
    inventory.to_csv(OUT / "artifact_inventory.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--force-ratings", action="store_true")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    ratings = collect_ratings(args.batch_size, args.force_ratings)
    model_results, details = evaluate_models(ratings)
    write_outputs(ratings, model_results, details)


if __name__ == "__main__":
    main()
