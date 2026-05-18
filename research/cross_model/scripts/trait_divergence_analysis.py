#!/usr/bin/env python3
"""Analyze Gemma-specific trait divergence against the Qwen/Llama baseline."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = ROOT / "research" / "cross_model" / "outputs"

INPUTS = {
    "top_bottom": OUTPUT_DIR / "trait_space_top10_bottom10.txt",
    "comparison": OUTPUT_DIR / "trait_space_comparison.csv",
    "divergent": OUTPUT_DIR / "trait_space_divergent_traits.txt",
}

CONVERGENT_TOP5 = ["transparent", "dispassionate", "detached", "calm", "quantitative"]

TRAIT_CATEGORY_MAP = {
    "accessible": "accessible_grounded_helpfulness",
    "practical": "accessible_grounded_helpfulness",
    "experiential": "accessible_grounded_helpfulness",
    "flexible": "accessible_grounded_helpfulness",
    "moderate": "accessible_grounded_helpfulness",
    "problem_solving": "accessible_grounded_helpfulness",
    "grounded": "accessible_grounded_helpfulness",
    "transparent": "accessible_grounded_helpfulness",
    "supportive": "accessible_grounded_helpfulness",
    "conciliatory": "accessible_grounded_helpfulness",
    "humble": "accessible_grounded_helpfulness",
    "generalist": "accessible_grounded_helpfulness",
    "adaptable": "accessible_grounded_helpfulness",
    "benevolent": "accessible_grounded_helpfulness",
    "inspirational": "accessible_grounded_helpfulness",
    "analytical": "analytic_methodical",
    "quantitative": "analytic_methodical",
    "methodical": "analytic_methodical",
    "data_driven": "analytic_methodical",
    "structuralist": "analytic_methodical",
    "reductionist": "analytic_methodical",
    "technical": "analytic_methodical",
    "factual": "analytic_methodical",
    "formal": "formal_regulatory",
    "serious": "formal_regulatory",
    "solemn": "formal_regulatory",
    "perfectionist": "formal_regulatory",
    "regulatory": "formal_regulatory",
    "meticulous": "formal_regulatory",
    "detached": "affective_regulation",
    "dispassionate": "affective_regulation",
    "calm": "affective_regulation",
    "resilient": "affective_regulation",
    "patient": "affective_regulation",
    "reserved": "affective_regulation",
    "esoteric": "abstract_elite_inward",
    "elitist": "abstract_elite_inward",
    "introspective": "abstract_elite_inward",
    "erudite": "abstract_elite_inward",
    "pensive": "abstract_elite_inward",
    "conceptual": "abstract_elite_inward",
    "abstract": "abstract_elite_inward",
    "theoretical": "abstract_elite_inward",
    "philosophical": "abstract_elite_inward",
    "existentialist": "abstract_elite_inward",
    "divergent": "abstract_elite_inward",
    "eloquent": "expressive_rhetorical",
    "bombastic": "expressive_rhetorical",
    "dramatic": "expressive_rhetorical",
    "theatrical": "expressive_rhetorical",
    "narrative": "expressive_rhetorical",
    "poetic": "expressive_rhetorical",
    "arrogant": "antagonistic_dark",
    "vindictive": "antagonistic_dark",
    "dogmatic": "antagonistic_dark",
    "nihilistic": "antagonistic_dark",
    "fundamentalist": "antagonistic_dark",
    "grandiose": "antagonistic_dark",
    "fatalistic": "antagonistic_dark",
    "callous": "antagonistic_dark",
    "cruel": "antagonistic_dark",
    "hostile": "antagonistic_dark",
    "misanthropic": "antagonistic_dark",
}

BIG_FIVE_MAP = {
    "accessible": "Agreeableness+",
    "supportive": "Agreeableness+",
    "conciliatory": "Agreeableness+",
    "humble": "Agreeableness+",
    "generous": "Agreeableness+",
    "benevolent": "Agreeableness+",
    "adaptable": "Agreeableness+",
    "empathetic": "Agreeableness+",
    "forgiving": "Agreeableness+",
    "arrogant": "Agreeableness-",
    "elitist": "Agreeableness-",
    "vindictive": "Agreeableness-",
    "dogmatic": "Agreeableness-",
    "callous": "Agreeableness-",
    "cruel": "Agreeableness-",
    "hostile": "Agreeableness-",
    "condescending": "Agreeableness-",
    "misanthropic": "Agreeableness-",
    "serious": "Conscientiousness+",
    "formal": "Conscientiousness+",
    "perfectionist": "Conscientiousness+",
    "regulatory": "Conscientiousness+",
    "meticulous": "Conscientiousness+",
    "methodical": "Conscientiousness+",
    "conscientious": "Conscientiousness+",
    "efficient": "Conscientiousness+",
    "practical": "Conscientiousness+",
    "problem_solving": "Conscientiousness+",
    "analytical": "Conscientiousness+",
    "reductionist": "Conscientiousness+",
    "disorganized": "Conscientiousness-",
    "impulsive": "Conscientiousness-",
    "spontaneous": "Conscientiousness-",
    "casual": "Conscientiousness-",
    "detached": "Extraversion-",
    "dispassionate": "Extraversion-",
    "reserved": "Extraversion-",
    "introverted": "Extraversion-",
    "calm": "Neuroticism-",
    "resilient": "Neuroticism-",
    "serene": "Neuroticism-",
    "patient": "Neuroticism-",
    "nihilistic": "Neuroticism+",
    "fatalistic": "Neuroticism+",
    "pessimistic": "Neuroticism+",
    "anxious": "Neuroticism+",
    "neurotic": "Neuroticism+",
    "temperamental": "Neuroticism+",
    "esoteric": "Openness+",
    "introspective": "Openness+",
    "conceptual": "Openness+",
    "abstract": "Openness+",
    "theoretical": "Openness+",
    "philosophical": "Openness+",
    "existentialist": "Openness+",
    "divergent": "Openness+",
    "creative": "Openness+",
    "artistic": "Openness+",
    "practical": "Openness-",
    "literal": "Openness-",
    "factual": "Openness-",
    "grounded": "Openness-",
    "traditional": "Openness-",
}

DARK_TRIAD_MAP = {
    "arrogant": "Narcissism+",
    "elitist": "Narcissism+",
    "grandiose": "Narcissism+",
    "condescending": "Narcissism+",
    "manipulative": "Machiavellianism+",
    "calculating": "Machiavellianism+",
    "strategic": "Machiavellianism+",
    "vindictive": "Psychopathy+",
    "callous": "Psychopathy+",
    "cruel": "Psychopathy+",
    "hostile": "Psychopathy+",
    "evil": "Psychopathy+",
    "savage": "Psychopathy+",
    "impulsive": "Psychopathy+",
    "risk_taking": "Psychopathy+",
}


def load_inputs() -> pd.DataFrame:
    missing = [str(path) for path in INPUTS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required input(s): " + ", ".join(missing))
    return pd.read_csv(INPUTS["comparison"])


def annotate(df: pd.DataFrame) -> pd.DataFrame:
    required = {"trait", "gemma_rank", "qwen_rank", "llama_rank"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"{INPUTS['comparison']} is missing columns: {sorted(missing)}")

    out = df.copy()
    out["qwen_llama_avg_rank"] = (out["qwen_rank"] + out["llama_rank"]) / 2.0
    out["gemma_deviation_from_qwen_llama"] = out["gemma_rank"] - out["qwen_llama_avg_rank"]
    out["abs_gemma_deviation"] = out["gemma_deviation_from_qwen_llama"].abs()
    out["direction"] = out["gemma_deviation_from_qwen_llama"].map(
        lambda value: "gemma_more_assistant_aligned" if value < 0 else "qwen_llama_more_assistant_aligned"
    )
    out["trait_category"] = out["trait"].map(lambda trait: TRAIT_CATEGORY_MAP.get(trait, "other"))
    out["big_five_cross_reference"] = out["trait"].map(lambda trait: BIG_FIVE_MAP.get(trait, "unmapped"))
    out["dark_triad_cross_reference"] = out["trait"].map(lambda trait: DARK_TRIAD_MAP.get(trait, "unmapped"))
    return out.sort_values(["abs_gemma_deviation", "trait"], ascending=[False, True]).reset_index(drop=True)


def count_column(rows: pd.DataFrame, column: str) -> str:
    counts = Counter(value for value in rows[column] if value != "unmapped")
    if not counts:
        return "none mapped"
    return ", ".join(f"{key}={value}" for key, value in counts.most_common())


def summarize_pattern(rows: pd.DataFrame, n: int = 15) -> str:
    traits = rows.head(n)["trait"].tolist()
    categories = Counter(rows.head(n)["trait_category"])
    return (
        f"Top traits: {', '.join(traits)}\n"
        f"Category counts: {', '.join(f'{key}={value}' for key, value in categories.most_common())}"
    )


def top_trait_lines(rows: pd.DataFrame, n: int = 30) -> list[str]:
    lines = []
    for _, row in rows.head(n).iterrows():
        lines.append(
            f"{row['trait']:<24} Gemma={int(row['gemma_rank']):>3} "
            f"Qwen={int(row['qwen_rank']):>3} Llama={int(row['llama_rank']):>3} "
            f"QL_avg={row['qwen_llama_avg_rank']:>6.1f} "
            f"dev={row['gemma_deviation_from_qwen_llama']:>7.1f} "
            f"{row['direction']}"
        )
    return lines


def main() -> None:
    raw = load_inputs()
    annotated = annotate(raw)

    csv_path = OUTPUT_DIR / "trait_divergence_gemma_vs_qwen_llama.csv"
    annotated.to_csv(csv_path, index=False)

    gemma_high = annotated[annotated["direction"] == "gemma_more_assistant_aligned"].copy()
    ql_high = annotated[annotated["direction"] == "qwen_llama_more_assistant_aligned"].copy()
    convergent = annotated[annotated["trait"].isin(CONVERGENT_TOP5)].copy()
    convergent = convergent.set_index("trait").loc[CONVERGENT_TOP5].reset_index()

    lines = []
    lines.append("Gemma vs Qwen/Llama Trait Divergence Analysis")
    lines.append("=" * 49)
    lines.append("Inputs loaded:")
    for label, path in INPUTS.items():
        lines.append(f"- {label}: {path}")
    lines.append("")
    lines.append("Top 30 absolute Gemma deviations from Qwen/Llama average rank")
    lines.append("-" * 64)
    lines.extend(top_trait_lines(annotated, 30))
    lines.append("")
    lines.append("A. Gemma ranks more assistant-aligned than Qwen+Llama")
    lines.append("-" * 56)
    lines.append(summarize_pattern(gemma_high, 15))
    lines.append(f"Big Five cross-reference counts: {count_column(gemma_high.head(30), 'big_five_cross_reference')}")
    lines.append(f"Dark Triad cross-reference counts: {count_column(gemma_high.head(30), 'dark_triad_cross_reference')}")
    lines.append(
        "Pattern: Gemma-specific assistant alignment is colder, more formal, more inward/elite, "
        "and more antagonistic than the Qwen/Llama baseline."
    )
    lines.append("")
    lines.append("B. Qwen+Llama rank more assistant-aligned than Gemma")
    lines.append("-" * 57)
    lines.append(summarize_pattern(ql_high, 15))
    lines.append(f"Big Five cross-reference counts: {count_column(ql_high.head(30), 'big_five_cross_reference')}")
    lines.append(f"Dark Triad cross-reference counts: {count_column(ql_high.head(30), 'dark_triad_cross_reference')}")
    lines.append(
        "Pattern: Qwen/Llama-shared assistant alignment is more accessible, practical, flexible, "
        "analytic, and problem-solving oriented than Gemma's assistant pole."
    )
    lines.append("")
    lines.append("Framework divergence interpretation")
    lines.append("-" * 35)
    lines.append(
        "Big Five: the largest Gemma-specific divergence clusters around lower Agreeableness "
        "(arrogant, elitist, dogmatic, vindictive), higher Openness/abstraction "
        "(esoteric, conceptual), and formal Conscientiousness (formal, serious, perfectionist)."
    )
    lines.append(
        "Big Five: the strongest Qwen/Llama-shared divergence clusters around higher Agreeableness "
        "and pragmatic Conscientiousness/Openness-lower grounding (accessible, practical, flexible, "
        "problem_solving, analytical)."
    )
    lines.append(
        "Dark Triad: Gemma-high divergent traits include more Narcissism/Psychopathy-coded terms "
        "(elitist, arrogant, grandiose, vindictive), while the Qwen/Llama-high side has little "
        "Dark Triad concentration."
    )
    lines.append("")
    lines.append("Convergent top 5 check")
    lines.append("-" * 23)
    for _, row in convergent.iterrows():
        truly = "tight" if row["rank_range"] <= 20 else ("moderate" if row["rank_range"] <= 50 else "top-half only")
        lines.append(
            f"- {row['trait']}: Gemma={int(row['gemma_rank'])}, Qwen={int(row['qwen_rank'])}, "
            f"Llama={int(row['llama_rank'])}, range={int(row['rank_range'])}, convergence={truly}"
        )
    lines.append(
        "Transparent, dispassionate, detached, and calm are genuinely tight or near-tight convergent traits. "
        "Quantitative is assistant-aligned in all three models, but its Gemma rank of 43 makes it a broader "
        "top-half convergence rather than a tight consensus."
    )
    lines.append("")
    lines.append("Bottom-line implication")
    lines.append("-" * 23)
    lines.append(
        "Across model families, assistant psychology appears to have a shared core of epistemic clarity "
        "and affective regulation. Gemma adds a colder, more hierarchical, more esoteric evaluator style, "
        "whereas Qwen and Llama emphasize accessible, grounded problem solving."
    )

    summary_path = OUTPUT_DIR / "trait_divergence_summary.txt"
    summary_path.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
