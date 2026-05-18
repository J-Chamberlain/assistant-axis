#!/usr/bin/env python3
"""Analyze Gemma-specific rank divergence from the Qwen/Llama baseline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / "research" / "cross_model" / "outputs" / "three_model_ranking_comparison.csv"
OUTPUT_DIR = ROOT / "research" / "cross_model" / "outputs"
DIVERGENCE_CSV = OUTPUT_DIR / "gemma_divergence_from_qwen_llama.csv"
SUMMARY_TXT = OUTPUT_DIR / "gemma_divergence_summary.txt"

TARGET_ROLES = ["virus", "simulacrum", "instructor", "trainer"]


def ranks_from_side_by_side(df: pd.DataFrame, role_col: str) -> dict[str, int]:
    """Return role -> 1-indexed rank from a side-by-side ranking column."""
    return {role: int(rank) for rank, role in zip(df["rank"], df[role_col])}


def build_divergence_table(df: pd.DataFrame) -> pd.DataFrame:
    gemma = ranks_from_side_by_side(df, "gemma_role")
    qwen = ranks_from_side_by_side(df, "qwen_role")
    llama = ranks_from_side_by_side(df, "llama_role")

    roles = sorted(set(gemma) & set(qwen) & set(llama))
    records = []
    for role in roles:
        qwen_llama_avg = (qwen[role] + llama[role]) / 2
        deviation = gemma[role] - qwen_llama_avg
        records.append(
            {
                "role": role,
                "gemma_rank": gemma[role],
                "qwen_rank": qwen[role],
                "llama_rank": llama[role],
                "qwen_llama_avg_rank": qwen_llama_avg,
                "gemma_deviation": deviation,
                "abs_gemma_deviation": abs(deviation),
                "direction": "gemma_lower_ranked"
                if deviation > 0
                else "gemma_higher_ranked",
            }
        )

    return (
        pd.DataFrame(records)
        .sort_values(["abs_gemma_deviation", "role"], ascending=[False, True])
        .reset_index(drop=True)
    )


def format_table(rows: pd.DataFrame, columns: list[str]) -> str:
    return rows[columns].to_string(index=False, float_format=lambda x: f"{x:.1f}")


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing required input: {INPUT}")

    df = pd.read_csv(INPUT)
    divergence = build_divergence_table(df)
    divergence.to_csv(DIVERGENCE_CSV, index=False)

    gemma_high = (
        divergence[divergence["gemma_deviation"] < 0]
        .sort_values(["gemma_deviation", "role"], ascending=[True, True])
        .head(15)
    )
    gemma_low = (
        divergence[divergence["gemma_deviation"] > 0]
        .sort_values(["gemma_deviation", "role"], ascending=[False, True])
        .head(15)
    )
    top30 = divergence.head(30)
    target_rows = divergence.set_index("role").loc[TARGET_ROLES].reset_index()

    summary = f"""Gemma Divergence from Qwen-Llama Baseline
===========================================

Input: {INPUT.relative_to(ROOT)}
Output CSV: {DIVERGENCE_CSV.relative_to(ROOT)}

Interpretation of deviation:
  gemma_deviation = gemma_rank - mean(qwen_rank, llama_rank)
  Negative deviation means Gemma ranks the role higher / more assistant-aligned.
  Positive deviation means Gemma ranks the role lower than the Qwen-Llama baseline.

Top 30 Most Divergent Roles by Absolute Gemma Deviation
-------------------------------------------------------
{format_table(top30, ["role", "gemma_rank", "qwen_rank", "llama_rank", "qwen_llama_avg_rank", "gemma_deviation"])}

Group A: Gemma-Specific Assistant-Aligned Roles
-----------------------------------------------
{format_table(gemma_high, ["role", "gemma_rank", "qwen_llama_avg_rank", "gemma_deviation"])}

Pattern:
Gemma-high divergent roles are not simply domain experts. The largest absolute
deviations are dominated by rigid, abstract, artificial, or systematic identities
such as simulacrum, purist, zealot, stoic, virus, traditionalist, hive, and
crystalline. This broadens the earlier domain-expert interpretation: Gemma's
assistant pole appears unusually sensitive to non-social order, constraint,
replication, and internally rigid structure, with hard-science and legal experts
forming one visible subset of that larger pattern.

Group B: Roles Qwen+Llama Rank Higher than Gemma
------------------------------------------------
{format_table(gemma_low, ["role", "gemma_rank", "qwen_llama_avg_rank", "gemma_deviation"])}

Pattern:
Gemma-low roles are dominated by instructional, coaching, organizing, and interpersonal
occupational roles. These are the roles Qwen and Llama treat as strongly assistant-like
but Gemma pushes downward, suggesting the Qwen-Llama baseline is closer to an ordinary
assistant/social-professional interpretation while Gemma privileges impersonal
procedural expertise.

Specified Role Checks
---------------------
{format_table(target_rows, ["role", "gemma_rank", "qwen_rank", "llama_rank", "qwen_llama_avg_rank", "gemma_deviation"])}

Conclusion
----------
The domain-expert vs occupational distinction holds most strongly on the Gemma-low
side: Qwen and Llama converge on instructors, trainers, planners, reviewers, and
organizers that Gemma ranks much lower. On the Gemma-high side, the pattern is
broader than domain expertise: Gemma elevates rigid, abstract, artificial, and
systematic identities. For the corpus-vs-process hypothesis, this suggests the
assistant-adjacent attractor may be general, but Gemma's training distribution or
vector extraction geometry has rotated that attractor toward impersonal structure
and away from literal assistance.
"""

    SUMMARY_TXT.write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
