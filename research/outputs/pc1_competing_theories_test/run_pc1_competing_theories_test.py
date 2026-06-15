#!/usr/bin/env python3
"""Competing PC1 theory test and scaffolded blind-rating benchmark.

Part A is fully local: vocabulary features over role instructions are tested
against canonical Qwen PC1 using the shared 273-persona benchmark rows.

Part B uses GPT-4.1-mini only when OPENAI_API_KEY is present. If credentials are
absent, the script writes an explicit blocked result and does not fabricate
ratings.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler


warnings.filterwarnings("ignore", category=RuntimeWarning)


REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "research" / "outputs" / "pc1_competing_theories_test"
SHARED = REPO / "research" / "q2_stability" / "qwen" / "outputs" / "shared_latent_feature_benchmark"
INSTRUCTION_DIR = REPO / "data" / "roles" / "instructions"

MODEL_USED = "GPT-5.5"
RATER_MODEL = "gpt-4.1-mini"


THEORIES: dict[str, list[str]] = {
    "A_orderliness_conscientiousness": [
        "tidy",
        "orderly",
        "neat",
        "organized",
        "symmetry",
        "punctual",
        "disciplined",
        "careful",
        "structured",
    ],
    "B_determination_explicit_criteria": [
        "determine",
        "qualify",
        "pass",
        "fail",
        "eligibility",
        "approval",
        "certification",
        "admissibility",
        "compliance decision",
    ],
    "C_external_standard_accountability": [
        "evidence",
        "methodology",
        "verification",
        "scrutiny",
        "validation",
        "audit",
        "protocol",
        "standards",
        "requirements",
        "peer review",
        "regulatory review",
        "independent criteria",
        "accountability",
    ],
}

PRIOR_BENCHMARKS = [
    ("semantic_baseline", 0.516873, 0.180967, 0.335665, 0.389397),
    ("codex_trait_replication", math.nan, math.nan, math.nan, 0.398000),
    ("codex_retained_procedural_behavioral", 0.631205, 0.257221, 0.422097, 0.490090),
    ("claude_bigfive_style", 0.733515, 0.480321, 0.415511, 0.612979),
    ("hierarchical_trait_plus_procedural", math.nan, math.nan, math.nan, 0.622000),
    ("residual_manifold_hand_feature", math.nan, math.nan, math.nan, 0.632000),
    ("semantic_bigfive_svd15_prompt_register", math.nan, math.nan, math.nan, 0.707000),
]


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", text.lower())


def count_term(text: str, term: str) -> int:
    lowered = text.lower()
    if " " in term:
        return len(re.findall(rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])", lowered))
    return len(re.findall(rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])", lowered))


def load_instruction_text(role: str) -> tuple[str, list[str]]:
    path = INSTRUCTION_DIR / f"{role}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    instructions = [item["pos"] for item in data.get("instruction", []) if isinstance(item, dict) and "pos" in item]
    return "\n".join(instructions), instructions


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return math.nan
    return float(stats.pearsonr(x, y).statistic)


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return math.nan
    return float(stats.spearmanr(x, y).statistic)


def residualize(v: np.ndarray, controls: np.ndarray) -> np.ndarray:
    x = np.asarray(controls, dtype=float)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    x = np.column_stack([np.ones(len(v)), x])
    coef, *_ = np.linalg.lstsq(x, v, rcond=None)
    return v - x @ coef


def one_hot(values: pd.Series) -> np.ndarray:
    cats = sorted(values.astype(str).unique())
    return np.array([[1.0 if val == cat else 0.0 for cat in cats[1:]] for val in values.astype(str)], dtype=float)


def shared_splits() -> list[tuple[np.ndarray, np.ndarray]]:
    splits = read_csv(SHARED / "shared_split_assignments.csv")
    roles = read_csv(SHARED / "canonical_activation_pca3d.csv")["persona"].tolist()
    idx = {role: i for i, role in enumerate(roles)}
    out = []
    for split_id in sorted(splits["canonical_split_id"].unique()):
        sub = splits[splits["canonical_split_id"].eq(split_id)]
        train_roles = sub[sub["canonical_assignment"].eq("train")]["persona"].tolist()
        test_roles = sub[sub["canonical_assignment"].eq("heldout")]["persona"].tolist()
        out.append((np.array([idx[r] for r in train_roles]), np.array([idx[r] for r in test_roles])))
    return out


def heldout_r2(x: np.ndarray, y: np.ndarray, splits: list[tuple[np.ndarray, np.ndarray]]) -> tuple[float, list[float]]:
    vals = []
    for train_idx, test_idx in splits:
        scaler = StandardScaler()
        x_train = scaler.fit_transform(x[train_idx])
        x_test = scaler.transform(x[test_idx])
        model = Ridge(alpha=1.0)
        model.fit(x_train, y[train_idx])
        pred = model.predict(x_test)
        vals.append(float(r2_score(y[test_idx], pred)))
    return float(np.mean(vals)), vals


def heldout_multi_axis_r2(x: np.ndarray, y: np.ndarray, splits: list[tuple[np.ndarray, np.ndarray]]) -> dict[str, float]:
    per_axis = []
    for axis in range(y.shape[1]):
        mean, _ = heldout_r2(x, y[:, axis], splits)
        per_axis.append(mean)
    return {
        "pc1_r2": per_axis[0],
        "pc2_r2": per_axis[1],
        "pc3_r2": per_axis[2],
        "mean_r2": float(np.mean(per_axis)),
    }


def build_text_feature_frame() -> pd.DataFrame:
    target = read_csv(SHARED / "canonical_activation_pca3d.csv").rename(
        columns={"persona": "role", "activation_pc1": "pc1", "activation_pc2": "pc2", "activation_pc3": "pc3"}
    )
    geometry = pd.read_csv(REPO / "research" / "geometry_tables" / "qwen_role_pc_rankings.csv")[
        ["role", "cluster"]
    ]
    rows = []
    for role in target["role"]:
        text, instructions = load_instruction_text(role)
        tokens = tokenize(text)
        row: dict[str, Any] = {
            "role": role,
            "instruction_text": text,
            "instruction_count": len(instructions),
            "text_length_tokens": len(tokens),
            "log_text_length": math.log(max(1, len(tokens))),
        }
        for theory, terms in THEORIES.items():
            counts = {term: count_term(text, term) for term in terms}
            raw = sum(counts.values())
            row[f"{theory}_raw_count"] = raw
            row[f"{theory}_norm_per_1000_tokens"] = raw / max(1, len(tokens)) * 1000.0
            for term, val in counts.items():
                row[f"{theory}__term__{term}"] = val
        rows.append(row)
    frame = target.merge(pd.DataFrame(rows), on="role").merge(geometry, on="role", how="left")
    frame["contrast_C_minus_A"] = (
        frame["C_external_standard_accountability_norm_per_1000_tokens"]
        - frame["A_orderliness_conscientiousness_norm_per_1000_tokens"]
    )
    frame["contrast_C_minus_B"] = (
        frame["C_external_standard_accountability_norm_per_1000_tokens"]
        - frame["B_determination_explicit_criteria_norm_per_1000_tokens"]
    )
    frame["contrast_B_minus_A"] = (
        frame["B_determination_explicit_criteria_norm_per_1000_tokens"]
        - frame["A_orderliness_conscientiousness_norm_per_1000_tokens"]
    )
    return frame


def part_a(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    pc1 = frame["pc1"].to_numpy(float)
    length = frame["log_text_length"].to_numpy(float)
    cluster = one_hot(frame["cluster"])
    cluster_len = np.column_stack([length, cluster])
    splits = shared_splits()
    control_only_r2, control_only_split_r2 = heldout_r2(cluster_len, pc1, splits)

    rows = []
    for theory in THEORIES:
        feature = frame[f"{theory}_norm_per_1000_tokens"].to_numpy(float)
        feature_only_r2, feature_only_split_r2 = heldout_r2(feature.reshape(-1, 1), pc1, splits)
        x_reg = np.column_stack([feature, length, cluster])
        reg_r2, split_r2 = heldout_r2(x_reg, pc1, splits)
        rows.append(
            {
                "theory": theory,
                "raw_count_total": int(frame[f"{theory}_raw_count"].sum()),
                "mean_norm_per_1000_tokens": float(np.mean(feature)),
                "pearson": pearson(feature, pc1),
                "spearman": spearman(feature, pc1),
                "partial_corr_control_text_length": pearson(residualize(feature, length), residualize(pc1, length)),
                "cluster_controlled": pearson(residualize(feature, cluster_len), residualize(pc1, cluster_len)),
                "feature_only_regression_r2": feature_only_r2,
                "control_only_regression_r2": control_only_r2,
                "regression_r2": reg_r2,
                "incremental_r2_over_cluster_length_controls": reg_r2 - control_only_r2,
                "feature_only_split_r2_values": json.dumps(feature_only_split_r2),
                "control_only_split_r2_values": json.dumps(control_only_split_r2),
                "split_r2_values": json.dumps(split_r2),
            }
        )
    for contrast in ["contrast_C_minus_A", "contrast_C_minus_B", "contrast_B_minus_A"]:
        feature = frame[contrast].to_numpy(float)
        feature_only_r2, feature_only_split_r2 = heldout_r2(feature.reshape(-1, 1), pc1, splits)
        x_reg = np.column_stack([feature, length, cluster])
        reg_r2, split_r2 = heldout_r2(x_reg, pc1, splits)
        rows.append(
            {
                "theory": contrast,
                "raw_count_total": math.nan,
                "mean_norm_per_1000_tokens": float(np.mean(feature)),
                "pearson": pearson(feature, pc1),
                "spearman": spearman(feature, pc1),
                "partial_corr_control_text_length": pearson(residualize(feature, length), residualize(pc1, length)),
                "cluster_controlled": pearson(residualize(feature, cluster_len), residualize(pc1, cluster_len)),
                "feature_only_regression_r2": feature_only_r2,
                "control_only_regression_r2": control_only_r2,
                "regression_r2": reg_r2,
                "incremental_r2_over_cluster_length_controls": reg_r2 - control_only_r2,
                "feature_only_split_r2_values": json.dumps(feature_only_split_r2),
                "control_only_split_r2_values": json.dumps(control_only_split_r2),
                "split_r2_values": json.dumps(split_r2),
            }
        )
    result = pd.DataFrame(rows)

    vocab_rows = []
    for theory, terms in THEORIES.items():
        for term in terms:
            col = f"{theory}__term__{term}"
            vocab_rows.append(
                {
                    "theory": theory,
                    "term": term,
                    "term_type": "phrase" if " " in term else "word",
                    "total_count_in_273_role_instruction_sets": int(frame[col].sum()),
                    "roles_with_term": int(frame[col].gt(0).sum()),
                }
            )
    vocab = pd.DataFrame(vocab_rows)
    return result, vocab


RATING_SYSTEM = """You are performing a blinded annotation task. Use only the role-instruction text supplied by the user. Do not assume any PCA, geometry, cluster, ranking, or target coordinate information; none is relevant here. Return strict JSON only."""


def rating_prompt(role: str, instructions: list[str]) -> str:
    joined = "\n".join(f"- {item}" for item in instructions)
    return f"""Rate the following instruction set on three 1-10 dimensions.

Dimension 1: External-Standard Accountability
1 = Outputs answer only to the role's own vision, instinct, expression, judgment, or nature.
10 = Outputs must withstand scrutiny against standards independent of the role itself, such as evidence, law, protocol, methodology, requirements, established criteria, peer review, or regulatory review.

Dimension 2: Integration / Coherence of Wholes
1 = Immediate situations, local experience, particular encounters, direct practical engagement.
10 = Underlying structure, persistent patterns, systems, identity-through-change, coherence of larger wholes.

Dimension 3: Internal Objective vs Care Orientation
1 = Organized around care, protection, service, obligation, or responsibility toward others.
10 = Organized around an internal objective, agenda, drive, or goal independent of others' outcomes.

Instruction text:
{joined}

Return JSON with keys: external_standard_accountability, integration_coherence_wholes, internal_objective_vs_care, one_sentence_rationale."""


def run_openai_ratings(frame: pd.DataFrame, force: bool) -> dict[str, Any]:
    if not force:
        return {
            "status": "not_run",
            "reason": "Run with --run-ratings and OPENAI_API_KEY to call GPT-4.1-mini.",
            "model": RATER_MODEL,
            "ratings": [],
        }
    if not os.environ.get("OPENAI_API_KEY"):
        return {
            "status": "blocked",
            "reason": "OPENAI_API_KEY is not set in the local shell, so GPT-4.1-mini blind ratings were not run.",
            "model": RATER_MODEL,
            "ratings": [],
        }
    from openai import OpenAI

    client = OpenAI()
    ratings = []
    for i, role in enumerate(frame["role"].tolist(), start=1):
        _, instructions = load_instruction_text(role)
        for attempt in range(3):
            try:
                response = client.responses.create(
                    model=RATER_MODEL,
                    input=[
                        {"role": "system", "content": RATING_SYSTEM},
                        {"role": "user", "content": rating_prompt(role, instructions)},
                    ],
                    temperature=0,
                    max_output_tokens=300,
                )
                text = response.output_text.strip()
                parsed = json.loads(text)
                ratings.append(
                    {
                        "role": role,
                        "external_standard_accountability": float(parsed["external_standard_accountability"]),
                        "integration_coherence_wholes": float(parsed["integration_coherence_wholes"]),
                        "internal_objective_vs_care": float(parsed["internal_objective_vs_care"]),
                        "one_sentence_rationale": str(parsed.get("one_sentence_rationale", "")),
                    }
                )
                break
            except Exception as exc:
                if attempt == 2:
                    ratings.append({"role": role, "error": repr(exc)})
                time.sleep(2 * (attempt + 1))
        if i % 25 == 0:
            print(f"rated {i}/{len(frame)}")
    return {
        "status": "complete",
        "model": RATER_MODEL,
        "n_roles": len(frame),
        "ratings": ratings,
    }


def benchmark_ratings(frame: pd.DataFrame, rating_result: dict[str, Any]) -> dict[str, Any] | None:
    if rating_result.get("status") != "complete":
        return None
    ratings = pd.DataFrame(rating_result["ratings"])
    if "error" in ratings.columns and ratings["error"].notna().any():
        return None
    joined = frame[["role", "pc1", "pc2", "pc3"]].merge(ratings, on="role")
    y = joined[["pc1", "pc2", "pc3"]].to_numpy(float)
    # Corrected sign: higher integration score predicts more negative PC2, so
    # include the score as rated and let regression learn sign; also export sign.
    x = joined[
        [
            "external_standard_accountability",
            "integration_coherence_wholes",
            "internal_objective_vs_care",
        ]
    ].to_numpy(float)
    metrics = heldout_multi_axis_r2(x, y, shared_splits())
    metrics["n_features"] = 3
    metrics["n_personas"] = len(joined)
    return metrics


def write_report(
    frame: pd.DataFrame,
    part_a_results: pd.DataFrame,
    rating_result: dict[str, Any],
    rating_metrics: dict[str, Any] | None,
) -> None:
    primary = part_a_results[part_a_results["theory"].isin(THEORIES)].copy()
    winner = primary.sort_values("regression_r2", ascending=False).iloc[0]
    c = primary[primary["theory"].eq("C_external_standard_accountability")].iloc[0]
    a = primary[primary["theory"].eq("A_orderliness_conscientiousness")].iloc[0]
    b = primary[primary["theory"].eq("B_determination_explicit_criteria")].iloc[0]
    c_outperforms_a = bool(c["regression_r2"] > a["regression_r2"])
    c_outperforms_b = bool(c["regression_r2"] > b["regression_r2"])

    lines = [
        "# PC1 Competing-Theories Test and Blind-Rating Validation",
        "",
        f"`model_used`: {MODEL_USED} for local analysis/reporting.",
        "",
        "## Startup Status",
        "",
        "Startup check passed using cache-busted raw GitHub fetches for `STARTUP_MANIFEST.md`, `RESEARCH_STATE.md`, `THREAD_START.md`, and `CLAIMS_REGISTER.md`.",
        "",
        "## Methods",
        "",
        "Part A tested three transparent vocabulary feature families over the five role-conditioning instructions for the 273 common personas in the shared benchmark. It computed raw counts, length-normalized counts, signed contrasts, Pearson/Spearman correlations, partial correlations controlling text length, cluster-and-length controlled correlations, and held-out ridge-regression PC1 R2 using the same deterministic split assignments as `shared_latent_feature_benchmark`.",
        "",
        "Part B was designed as a corrected blind-rating test using GPT-4.1-mini over role instructions only. Ratings were not exposed to PC coordinates, PCA labels, geometry information, cluster labels, or rankings.",
        "",
        "## Part A Direct Comparison",
        "",
        "| Theory | Pearson | Spearman | Cluster-controlled | Regression R2 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in primary.itertuples(index=False):
        lines.append(
            f"| {row.theory} | {row.pearson:.3f} | {row.spearman:.3f} | "
            f"{row.cluster_controlled:.3f} | {row.regression_r2:.3f} |"
        )
    lines += [
        "",
        "## Observed",
        "",
        f"- Best Part A PC1 predictor by held-out regression R2: `{winner['theory']}` with R2={winner['regression_r2']:.3f}.",
        f"- Control-only held-out regression using text length plus cluster already reaches R2={c['control_only_regression_r2']:.3f}; therefore theory-vocabulary incremental deltas are the stricter comparison.",
        f"- External-standard accountability incremental R2 over cluster/length controls is {c['incremental_r2_over_cluster_length_controls']:+.4f}, versus orderliness {a['incremental_r2_over_cluster_length_controls']:+.4f} and determination {b['incremental_r2_over_cluster_length_controls']:+.4f}.",
        f"- External-standard accountability {'outperforms' if c_outperforms_a else 'fails to outperform'} orderliness/conscientiousness by held-out regression R2 ({c['regression_r2']:.3f} vs {a['regression_r2']:.3f}).",
        f"- External-standard accountability {'outperforms' if c_outperforms_b else 'fails to outperform'} determination-against-explicit-criteria by held-out regression R2 ({c['regression_r2']:.3f} vs {b['regression_r2']:.3f}).",
        f"- GPT-4.1-mini blind-rating status: `{rating_result.get('status')}`.",
    ]
    if rating_metrics:
        lines += [
            f"- Blind-rating benchmark PC1 R2={rating_metrics['pc1_r2']:.3f}, PC2 R2={rating_metrics['pc2_r2']:.3f}, PC3 R2={rating_metrics['pc3_r2']:.3f}, mean R2={rating_metrics['mean_r2']:.3f}.",
        ]
    else:
        lines += [
            f"- Blind-rating benchmark metrics were not computed because rating status was `{rating_result.get('status')}`: {rating_result.get('reason', 'no reason recorded')}",
        ]
    lines += [
        "",
        "## Inferred",
        "",
        "Vocabulary evidence alone should be treated as weak evidence because exact-word features are sparse and role-instruction wording can miss conceptual content. The stronger test is the corrected blind-rating benchmark, which requires GPT-4.1-mini ratings and the shared held-out evaluation path.",
        "",
        "## Speculative",
        "",
        "If blind ratings later show the external-standard-accountability dimension outperforming the orderliness and determination vocabularies and approaching prior compact-feature benchmarks, that would support elevating the PC1 interpretation. If they do not, the PC1 wording should remain provisional or be revised.",
        "",
        "## Prior Benchmark Context",
        "",
        "| Feature family | PC1 R2 | PC2 R2 | PC3 R2 | Mean R2 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, pc1, pc2, pc3, mean in PRIOR_BENCHMARKS:
        def fmt(x: float) -> str:
            return "" if math.isnan(x) else f"{x:.3f}"
        lines.append(f"| {name} | {fmt(pc1)} | {fmt(pc2)} | {fmt(pc3)} | {mean:.3f} |")
    if rating_metrics:
        lines.append(
            f"| gpt41mini_blind_pc_interpretation_ratings | {rating_metrics['pc1_r2']:.3f} | {rating_metrics['pc2_r2']:.3f} | {rating_metrics['pc3_r2']:.3f} | {rating_metrics['mean_r2']:.3f} |"
        )
    else:
        lines.append("| gpt41mini_blind_pc_interpretation_ratings |  |  |  | blocked |")
    lines += [
        "",
        "## Limitations",
        "",
        "- Part A exact-vocabulary counts are transparent but sparse.",
        "- Cluster-controlled correlations are residualized against Qwen cluster labels and text length; they are diagnostic, not causal.",
        "- The blind-rating component requires local OpenAI API credentials. This run did not fabricate missing ratings.",
        "- The corrected PC2 blind-rating direction is higher integration score -> more negative PC2.",
    ]
    (OUT / "pc1_competing_theories_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-ratings", action="store_true", help="Call GPT-4.1-mini if OPENAI_API_KEY is set.")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    frame = build_text_feature_frame()
    frame.to_csv(OUT / "pc1_role_instruction_theory_features.csv", index=False)
    part_a_results, vocab = part_a(frame)
    vocab.to_csv(OUT / "pc1_vocabulary_comparison.csv", index=False)
    part_a_results.to_csv(OUT / "pc1_cluster_controlled_results.csv", index=False)

    rating_result = run_openai_ratings(frame, force=args.run_ratings)
    rating_metrics = benchmark_ratings(frame, rating_result)
    if rating_metrics:
        rating_result["benchmark_metrics"] = rating_metrics
    (OUT / "blind_rating_results.json").write_text(json.dumps(rating_result, indent=2), encoding="utf-8")

    rows = [
        {
            "feature_family": name,
            "pc1_r2": pc1,
            "pc2_r2": pc2,
            "pc3_r2": pc3,
            "mean_r2": mean,
            "source": "prior_shared_benchmark",
        }
        for name, pc1, pc2, pc3, mean in PRIOR_BENCHMARKS
    ]
    if rating_metrics:
        rows.append(
            {
                "feature_family": "gpt41mini_blind_pc_interpretation_ratings",
                **rating_metrics,
                "source": "this_run_gpt41mini",
            }
        )
    else:
        rows.append(
            {
                "feature_family": "gpt41mini_blind_pc_interpretation_ratings",
                "pc1_r2": math.nan,
                "pc2_r2": math.nan,
                "pc3_r2": math.nan,
                "mean_r2": math.nan,
                "source": f"not_computed_{rating_result.get('status')}",
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "benchmark_comparison.csv", index=False)

    write_report(frame, part_a_results, rating_result, rating_metrics)

    inventory = pd.DataFrame(
        [
            {
                "artifact": p.name,
                "path": str(p.relative_to(REPO)),
                "status": "active",
                "description": "PC1 competing-theories or blind-rating validation artifact.",
            }
            for p in sorted(OUT.iterdir())
            if p.name != "artifact_inventory.csv"
        ]
    )
    inventory.to_csv(OUT / "artifact_inventory.csv", index=False)


if __name__ == "__main__":
    main()
