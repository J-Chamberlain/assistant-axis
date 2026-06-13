#!/usr/bin/env python3
"""Build prompt-level diagnostics for no-label elicitation Run 2."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "research" / "outputs" / "no_label_elicitation_run2_prompt_diagnostics"
RUN2 = REPO / "research" / "outputs" / "no_label_elicitation_run2"
RUN1 = REPO / "research" / "outputs" / "no_label_elicitation_validation"

BARE_QWEN = {
    "pc1": 23.50993662490646,
    "pc2": 14.040867457612329,
    "pc3": -2.4601124846522726,
}


def qnum(prompt_id: str) -> int:
    return int(prompt_id.rsplit("_", 1)[-1])


def pass_fail(value: float) -> str:
    return "pass" if value > 0 else "fail"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    run2 = pd.read_csv(RUN2 / "run2_prompt_mean_results.csv")
    run1 = pd.read_csv(RUN1 / "prompt_mean_results.csv")
    run1_catalog = pd.read_csv(RUN1 / "prompt_catalog_used.csv")
    pairwise = pd.read_csv(RUN2 / "run2_pairwise_effects.csv")

    pc1 = run2[run2["component"].eq("pc1_positive_replacement_family")].copy()
    pc1["pc"] = "PC1"
    pc1["direction"] = "positive"
    pc1["question_count"] = pc1["prompt_id"].map(qnum)
    pc1["display_id"] = pc1["question_count"].map(lambda i: f"PC1 positive {i}")
    pc1["target_delta_bare_qwen"] = pc1["mean_delta_bare_qwen_pc1"]
    pc1["directional_value_bare_qwen"] = pc1["target_delta_bare_qwen"]
    pc1["absolute_target_delta_bare_qwen"] = pc1["target_delta_bare_qwen"].abs()
    pc1["bare_qwen_direction_pass"] = pc1["directional_value_bare_qwen"].map(pass_fail)
    pc1 = pc1.sort_values("question_count")
    pc1_cols = [
        "display_id",
        "prompt_id",
        "question_count",
        "target_delta_bare_qwen",
        "directional_value_bare_qwen",
        "absolute_target_delta_bare_qwen",
        "bare_qwen_direction_pass",
        "mean_delta_assistant_pc1",
        "mean_pc1",
        "mean_pc2",
        "mean_pc3",
        "std_pc1",
        "std_pc2",
        "std_pc3",
        "prompt_text",
    ]
    pc1[pc1_cols].to_csv(OUT / "pc1_positive_replacement_ranked.csv", index=False)
    pc1_selected = pd.concat(
        [
            pc1[pc1["bare_qwen_direction_pass"].eq("fail")].sort_values("directional_value_bare_qwen"),
            pc1.sort_values("directional_value_bare_qwen", ascending=False).head(3),
        ],
        ignore_index=True,
    )
    pc1_selected["selection_reason"] = [
        *(["failed_vs_bare_qwen"] * int((pc1["bare_qwen_direction_pass"].eq("fail")).sum())),
        *(["strongest_vs_bare_qwen"] * 3),
    ]
    pc1_selected[["selection_reason", *pc1_cols]].to_csv(
        OUT / "pc1_positive_replacement_selected.csv", index=False
    )

    pc2 = run2[run2["component"].eq("pc2_negative_replacement_family")].copy()
    pc2["pc"] = "PC2"
    pc2["direction"] = "negative"
    pc2["question_count"] = pc2["prompt_id"].map(qnum)
    pc2["display_id"] = pc2["question_count"].map(lambda i: f"PC2 negative {i}")
    pc2["target_delta_bare_qwen"] = pc2["mean_delta_bare_qwen_pc2"]
    pc2["directional_value_bare_qwen"] = -pc2["target_delta_bare_qwen"]
    pc2["absolute_target_delta_bare_qwen"] = pc2["target_delta_bare_qwen"].abs()
    pc2["bare_qwen_direction_pass"] = pc2["directional_value_bare_qwen"].map(pass_fail)
    pc2["target_delta_assistant"] = pc2["mean_delta_assistant_pc2"]
    pc2["directional_value_assistant"] = -pc2["target_delta_assistant"]
    pc2["assistant_direction_pass"] = pc2["directional_value_assistant"].map(pass_fail)
    pc2 = pc2.sort_values("question_count")
    pc2_cols = [
        "display_id",
        "prompt_id",
        "question_count",
        "subanalysis_group",
        "target_delta_bare_qwen",
        "directional_value_bare_qwen",
        "absolute_target_delta_bare_qwen",
        "bare_qwen_direction_pass",
        "target_delta_assistant",
        "directional_value_assistant",
        "assistant_direction_pass",
        "mean_pc1",
        "mean_pc2",
        "mean_pc3",
        "std_pc1",
        "std_pc2",
        "std_pc3",
        "prompt_text",
    ]
    pc2[pc2_cols].to_csv(OUT / "pc2_negative_replacement_ranked.csv", index=False)

    pc2_best = pc2.sort_values("directional_value_bare_qwen", ascending=False).head(2).copy()
    pc2_best["selection_reason"] = "strongest_vs_bare_qwen"
    pc2_fail = pc2[pc2["bare_qwen_direction_pass"].eq("fail")].copy()
    pc2_fail["selection_reason"] = "failed_vs_bare_qwen"
    pc2_closest_pass = (
        pc2[pc2["bare_qwen_direction_pass"].eq("pass")]
        .sort_values("directional_value_bare_qwen")
        .head(1)
        .copy()
    )
    pc2_closest_pass["selection_reason"] = "closest_pass_vs_bare_qwen"
    pc2_assistant_fail = pc2[pc2["assistant_direction_pass"].eq("fail")].copy()
    pc2_assistant_fail["selection_reason"] = "failed_vs_assistant_centroid"
    pc2_selected = pd.concat(
        [pc2_best, pc2_fail, pc2_closest_pass, pc2_assistant_fail],
        ignore_index=True,
    ).drop_duplicates(["prompt_id", "selection_reason"])
    pc2_selected[["selection_reason", *pc2_cols]].to_csv(
        OUT / "pc2_negative_replacement_selected.csv", index=False
    )

    pc3_rows = []
    # Pair 1: A from Run 1 pc3_pos_05, B from Run 2 pc3_pair_01B.
    a1 = run1[run1["prompt_id"].eq("pc3_pos_05")].iloc[0]
    a1_text = run1_catalog[run1_catalog["prompt_id"].eq("pc3_pos_05")]["prompt_text"].iloc[0]
    b1 = run2[run2["prompt_id"].eq("pc3_pair_01B")].iloc[0]
    pc3_rows.append(
        {
            "pair_id": "pc3_pair_01",
            "comparison": "B_minus_A",
            "a_prompt_id": "pc3_pos_05",
            "b_prompt_id": "pc3_pair_01B",
            "a_source": "Run 1 no-label validation",
            "b_source": "Run 2",
            "delta_pc1_b_minus_a": b1["mean_pc1"] - a1["mean_pc1"],
            "delta_pc2_b_minus_a": b1["mean_pc2"] - a1["mean_pc2"],
            "delta_pc3_b_minus_a": b1["mean_pc3"] - a1["mean_pc3"],
            "directional_value_pc3": b1["mean_pc3"] - a1["mean_pc3"],
            "success": (b1["mean_pc3"] - a1["mean_pc3"]) > 0,
            "a_prompt_text": a1_text,
            "b_prompt_text": b1["prompt_text"],
        }
    )
    for _, row in pairwise[
        pairwise["component"].eq("pc3_minimal_pairs") & pairwise["status"].eq("complete")
    ].iterrows():
        a_prompt_id = f"{row['pair_id']}A"
        b_prompt_id = f"{row['pair_id']}B"
        a = run2[run2["prompt_id"].eq(a_prompt_id)].iloc[0]
        b = run2[run2["prompt_id"].eq(b_prompt_id)].iloc[0]
        pc3_rows.append(
            {
                "pair_id": row["pair_id"],
                "comparison": "B_minus_A",
                "a_prompt_id": a_prompt_id,
                "b_prompt_id": b_prompt_id,
                "a_source": "Run 2",
                "b_source": "Run 2",
                "delta_pc1_b_minus_a": row["delta_bare_qwen_pc1"],
                "delta_pc2_b_minus_a": row["delta_bare_qwen_pc2"],
                "delta_pc3_b_minus_a": row["delta_bare_qwen_pc3"],
                "directional_value_pc3": row["target_diff"],
                "success": str(row["success"]).lower() == "true",
                "a_prompt_text": a["prompt_text"],
                "b_prompt_text": b["prompt_text"],
            }
        )
    pc3 = pd.DataFrame(pc3_rows).sort_values("pair_id")
    pc3.to_csv(OUT / "pc3_cost_to_others_pairwise_with_run1.csv", index=False)

    # Figures.
    fig, axes = plt.subplots(3, 1, figsize=(13, 15), constrained_layout=True)
    colors = pc1["bare_qwen_direction_pass"].map({"pass": "#2ca25f", "fail": "#de2d26"})
    axes[0].bar(pc1["display_id"], pc1["directional_value_bare_qwen"], color=colors)
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("PC1+ replacement: target-axis movement vs bare Qwen")
    axes[0].set_ylabel("Delta PC1")
    axes[0].tick_params(axis="x", rotation=35)

    colors = pc2["bare_qwen_direction_pass"].map({"pass": "#2ca25f", "fail": "#de2d26"})
    axes[1].bar(pc2["display_id"], pc2["directional_value_bare_qwen"], color=colors)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("PC2- replacement: direction-corrected movement vs bare Qwen")
    axes[1].set_ylabel("-Delta PC2")
    axes[1].tick_params(axis="x", rotation=35)

    x = np.arange(len(pc3))
    width = 0.25
    axes[2].bar(x - width, pc3["delta_pc1_b_minus_a"], width, label="B-A PC1", color="#9ecae1")
    axes[2].bar(x, pc3["delta_pc2_b_minus_a"], width, label="B-A PC2", color="#bcbddc")
    axes[2].bar(x + width, pc3["delta_pc3_b_minus_a"], width, label="B-A PC3", color="#756bb1")
    axes[2].axhline(0, color="black", linewidth=0.8)
    axes[2].set_title("PC3 minimal pairs: cost-to-others minus cost-to-self")
    axes[2].set_ylabel("B - A mean coordinate")
    axes[2].set_xticks(x, pc3["pair_id"])
    axes[2].legend()
    fig.savefig(OUT / "run2_prompt_diagnostic_plots.png", dpi=180)
    plt.close(fig)

    summary = {
        "model_used": "GPT-5.5",
        "run2_prompt_mean_source": str((RUN2 / "run2_prompt_mean_results.csv").relative_to(REPO)),
        "run1_prompt_mean_source": str((RUN1 / "prompt_mean_results.csv").relative_to(REPO)),
        "bare_qwen_centroid": BARE_QWEN,
        "pc1_failed_prompt_ids": pc1[pc1["bare_qwen_direction_pass"].eq("fail")][
            "prompt_id"
        ].tolist(),
        "pc1_strongest_prompt_ids": pc1.sort_values(
            "directional_value_bare_qwen", ascending=False
        )["prompt_id"].head(3).tolist(),
        "pc2_failed_vs_bare_qwen": pc2[pc2["bare_qwen_direction_pass"].eq("fail")][
            "prompt_id"
        ].tolist(),
        "pc2_failed_vs_assistant": pc2[pc2["assistant_direction_pass"].eq("fail")][
            "prompt_id"
        ].tolist(),
        "pc3_pair_success_count": int(pc3["success"].sum()),
        "pc3_pair_count": int(len(pc3)),
    }
    (OUT / "run2_prompt_diagnostics_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    def md_table(df: pd.DataFrame, cols: list[str]) -> str:
        rows = df[cols].copy()

        def fmt(value: object) -> str:
            if isinstance(value, float):
                return f"{value:.3f}"
            if pd.isna(value):
                return ""
            return str(value).replace("\n", " ").replace("|", "\\|")

        header = "| " + " | ".join(cols) + " |"
        divider = "| " + " | ".join(["---"] * len(cols)) + " |"
        body = [
            "| " + " | ".join(fmt(row[col]) for col in cols) + " |"
            for _, row in rows.iterrows()
        ]
        return "\n".join([header, divider, *body])

    report = f"""# Run 2 Prompt-Level Diagnostics

Generated by `run_run2_prompt_diagnostics.py`.

## Sources

- Run 2 prompt means: `{summary['run2_prompt_mean_source']}`
- Run 1 prompt means for inherited PC3 pair A-side: `{summary['run1_prompt_mean_source']}`
- Bare-Qwen centroid: PC1={BARE_QWEN['pc1']:.3f}, PC2={BARE_QWEN['pc2']:.3f}, PC3={BARE_QWEN['pc3']:.3f}
- `model_used`: GPT-5.5

## PC1 Positive Replacement

The PC1+ replacement family passed the Run 2 family threshold relative to bare Qwen with 7/10 prompts moving positive on PC1. The three failures were `pc1_pos_r2_04`, `pc1_pos_r2_06`, and `pc1_pos_r2_09`; the three strongest were `pc1_pos_r2_07`, `pc1_pos_r2_05`, and `pc1_pos_r2_08`.

{md_table(pc1_selected, ['selection_reason', 'display_id', 'prompt_id', 'target_delta_bare_qwen', 'directional_value_bare_qwen', 'absolute_target_delta_bare_qwen', 'bare_qwen_direction_pass', 'prompt_text'])}

## PC2 Negative Replacement

The PC2- replacement family passed relative to bare Qwen with 9/10 prompts moving negative on PC2. The strongest two were `pc2_neg_r2_07` and `pc2_neg_r2_10`; `pc2_neg_r2_02` failed relative to bare Qwen; `pc2_neg_r2_03` was the closest pass relative to bare Qwen. Relative to the assistant-role centroid, `pc2_neg_r2_02` and `pc2_neg_r2_03` failed.

{md_table(pc2_selected, ['selection_reason', 'display_id', 'prompt_id', 'subanalysis_group', 'target_delta_bare_qwen', 'directional_value_bare_qwen', 'bare_qwen_direction_pass', 'target_delta_assistant', 'directional_value_assistant', 'assistant_direction_pass', 'prompt_text'])}

## PC3 Cost-To-Others Minimal Pairs

Pair 1 uses Run 1 `pc3_pos_05` as the cost-to-self A-side, as preregistered, and Run 2 `pc3_pair_01B` as the cost-to-others B-side. Across all five pairs, cost-to-others moved more positive on PC3 in {int(pc3['success'].sum())}/{len(pc3)} pairs.

{md_table(pc3, ['pair_id', 'a_prompt_id', 'b_prompt_id', 'delta_pc1_b_minus_a', 'delta_pc2_b_minus_a', 'delta_pc3_b_minus_a', 'directional_value_pc3', 'success'])}

## Diagnostic Notes

Observed: PC1+ failures were not simply weak positives; `pc1_pos_r2_06` and `pc1_pos_r2_09` moved substantially negative on PC1 relative to bare Qwen. The strongest PC1+ prompts involved access-control, signature-control, and grant-rule admissibility scenarios rather than arithmetic-only checking.

Observed: The only PC2- prompt failing relative to bare Qwen was the neighborhood prompt (`pc2_neg_r2_02`), which likely invited local social/place description despite the "beneath the surface" wording. `pc2_neg_r2_03` passed relative to bare Qwen but failed relative to the assistant-role centroid, making it baseline-sensitive.

Observed: PC3 pair 5 produced the largest positive PC3 cost-to-others effect but also a large negative PC1 shift. PC3 pair 3 failed, with the cost-to-others blame framing moving lower on PC3 than the self-blame version.

Inferred: The PC1+ results support the revised idea that positive PC1 is better elicited by explicit admissibility, compliance, access, signature, or documented-control decisions than by arithmetic correction alone.

Inferred: The PC2- results support integrative-whole wording when it avoids concrete scene immersion; prompts that sound like place-based observation can pull back toward positive PC2.

"""
    (OUT / "run2_prompt_diagnostics_report.md").write_text(report, encoding="utf-8")

    inventory = pd.DataFrame(
        [
            {
                "artifact": p.name,
                "path": str(p.relative_to(REPO)),
                "artifact_type": "table" if p.suffix == ".csv" else "report_or_figure",
                "source": "Run 2 prompt means; Run 1 prompt means for pc3_pair_01 A-side",
            }
            for p in sorted(OUT.iterdir())
            if p.name != "artifact_inventory.csv"
        ]
    )
    inventory.to_csv(OUT / "artifact_inventory.csv", index=False)


if __name__ == "__main__":
    main()
