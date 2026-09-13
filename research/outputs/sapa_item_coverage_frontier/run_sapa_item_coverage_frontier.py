#!/usr/bin/env python3
"""Build the aggregate-only SAPA item-coverage frontier.

The analysis uses response availability only. It does not score constructs,
impute responses, inspect model artifacts, or emit respondent-level data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUTPUT_REL = Path("research/outputs/sapa_item_coverage_frontier")
DICTIONARY_REL = Path(
    "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv"
)
RAW_TAB_NAME = "sapaTempData696items08dec2013thru26jul2014.tab"
RAW_ITEM_INFO_NAME = "ItemInfo696.csv"
EXPECTED_RESPONDENTS = 23_679
EXPECTED_ITEMS = 696
VALID_RESPONSE_CODES = ("1", "2", "3", "4", "5", "6")
MARGINAL_THRESHOLDS = (100, 99, 95, 90, 80, 70, 60, 50, 25, 20, 15, 10)
RELAXED_LEVELS = (0.95, 0.90, 0.80)
RAW_BASE = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, text=True, capture_output=True
    )
    return result.stdout.strip()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def pct(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 6)


def availability_to_bits(column: np.ndarray) -> int:
    packed = np.packbits(column, bitorder="little")
    return int.from_bytes(packed.tobytes(), "little")


def greedy_nested_order(
    available: np.ndarray, marginal_n: np.ndarray
) -> tuple[list[int], list[int], list[int]]:
    """Return order, strict counts, and exact-best tie counts.

    The candidate objective is expanded-panel complete-case N. Ties use larger
    marginal N and then smaller canonical dictionary position.
    """

    n_rows, n_items = available.shape
    item_bits = [availability_to_bits(available[:, j]) for j in range(n_items)]
    remaining = set(range(n_items))
    current = (1 << n_rows) - 1
    order: list[int] = []
    complete_counts: list[int] = []
    best_tie_counts: list[int] = []

    while remaining:
        scored = [(current & item_bits[j]).bit_count() for j in remaining]
        best_joint = max(scored)
        joint_ties = [j for j in remaining if (current & item_bits[j]).bit_count() == best_joint]
        best_marginal = max(int(marginal_n[j]) for j in joint_ties)
        finalists = [j for j in joint_ties if int(marginal_n[j]) == best_marginal]
        chosen = min(finalists)
        current &= item_bits[chosen]
        order.append(chosen)
        complete_counts.append(current.bit_count())
        best_tie_counts.append(len(finalists))
        remaining.remove(chosen)

    return order, complete_counts, best_tie_counts


def build_frontier(
    available: np.ndarray, order: list[int], strict_bit_counts: list[int]
) -> pd.DataFrame:
    n_rows = available.shape[0]
    answered = np.zeros(n_rows, dtype=np.int16)
    rows: list[dict[str, int | float | str]] = []
    for step, item_index in enumerate(order, 1):
        answered += available[:, item_index]
        strict_n = int(np.count_nonzero(answered == step))
        if strict_n != strict_bit_counts[step - 1]:
            raise AssertionError(f"Strict count mismatch at step {step}")
        row: dict[str, int | float | str] = {
            "panel_size": step,
            "added_item_id": "",
            "complete_n": strict_n,
            "complete_pct_total": pct(strict_n, n_rows),
        }
        for level in RELAXED_LEVELS:
            label = str(int(level * 100))
            required = int(math.ceil(level * step - 1e-12))
            count = int(np.count_nonzero(answered >= required))
            row[f"min_answered_for_{label}pct"] = required
            row[f"at_least_{label}pct_n"] = count
            row[f"at_least_{label}pct_total"] = pct(count, n_rows)
        rows.append(row)
    return pd.DataFrame(rows)


def threshold_rows(marginal_n: np.ndarray, n_rows: int) -> pd.DataFrame:
    rows = []
    for threshold in MARGINAL_THRESHOLDS:
        required = int(math.ceil(threshold / 100 * n_rows - 1e-12))
        count = int(np.count_nonzero(marginal_n >= required))
        rows.append(
            {
                "coverage_threshold_pct": threshold,
                "minimum_recorded_n": required,
                "items_meeting_threshold": count,
                "pct_of_696_items": round(100 * count / EXPECTED_ITEMS, 6),
            }
        )
    return pd.DataFrame(rows)


def first_at_or_below(frontier: pd.DataFrame, column: str, target: int) -> int | None:
    matches = frontier.loc[frontier[column] <= target, "panel_size"]
    return int(matches.iloc[0]) if len(matches) else None


def informative_sizes(frontier: pd.DataFrame) -> list[int]:
    # Every strict-count transition is empirically informative; add the last
    # positive and first-zero steps for each relaxed curve.
    sizes = {1, len(frontier)}
    strict = frontier["complete_n"].to_numpy()
    sizes.update((np.flatnonzero(np.r_[True, strict[1:] != strict[:-1]]) + 1).tolist())
    for column in ("complete_n", "at_least_95pct_n", "at_least_90pct_n", "at_least_80pct_n"):
        zero = first_at_or_below(frontier, column, 0)
        if zero is not None:
            sizes.update({max(1, zero - 1), zero})
    return sorted(sizes)


def render_figure(frontier: pd.DataFrame, output: Path) -> None:
    matplotlib.rcParams["svg.hashsalt"] = "aa12-sapa-item-coverage-frontier"
    plt.rcParams.update({"font.size": 10, "axes.titleweight": "bold"})
    colors = {
        "complete_n": "#14213d",
        "at_least_95pct_n": "#0077b6",
        "at_least_90pct_n": "#2a9d8f",
        "at_least_80pct_n": "#e76f51",
    }
    labels = {
        "complete_n": "100% complete",
        "at_least_95pct_n": "≥95% answered",
        "at_least_90pct_n": "≥90% answered",
        "at_least_80pct_n": "≥80% answered",
    }
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 8.4), constrained_layout=True)
    x = frontier["panel_size"]
    for column in colors:
        axes[0].plot(x, frontier[column], color=colors[column], lw=2.0, label=labels[column])
    axes[0].set(
        title="SAPA greedy nested item-coverage frontier",
        xlabel="Items in nested panel",
        ylabel="Respondents remaining",
        xlim=(1, len(frontier)),
    )
    axes[0].set_ylim(0, max(frontier["at_least_80pct_n"]) * 1.06)
    axes[0].grid(alpha=0.22)
    axes[0].legend(ncol=2, frameon=False)

    zoom_end = min(len(frontier), 50)
    early = frontier.loc[frontier.panel_size <= zoom_end]
    for column in colors:
        axes[1].plot(
            early["panel_size"],
            early[column],
            color=colors[column],
            lw=2.0,
            label=labels[column],
        )
    axes[1].set(
        title=f"Early-panel detail (first {zoom_end} nested items)",
        xlabel="Items in nested panel",
        ylabel="Respondents remaining (symlog)",
        xlim=(1, zoom_end),
    )
    axes[1].set_yscale("symlog", linthresh=10)
    axes[1].set_ylim(0, max(early["at_least_80pct_n"]) * 1.08)
    axes[1].grid(alpha=0.22, which="both")
    axes[1].text(
        0.995,
        0.02,
        "Availability-only greedy order; relaxed curves use the same nested panels. No imputation.",
        transform=axes[1].transAxes,
        ha="right",
        va="bottom",
        fontsize=8.5,
        color="#444444",
    )
    fig.savefig(output / "sapa_coverage_frontier.png", dpi=180, metadata={"Date": None})
    fig.savefig(output / "sapa_coverage_frontier.svg", metadata={"Date": None})
    plt.close(fig)


def markdown_table(frontier: pd.DataFrame, sizes: list[int]) -> str:
    chosen = frontier.set_index("panel_size").loc[sizes].reset_index()
    lines = [
        "| Items in nested panel | Complete respondents | Complete % | ≥95% answered | ≥90% answered | ≥80% answered |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in chosen.itertuples(index=False):
        lines.append(
            f"| {row.panel_size:,} | {row.complete_n:,} | {row.complete_pct_total:.3f}% | "
            f"{row.at_least_95pct_n:,} | {row.at_least_90pct_n:,} | {row.at_least_80pct_n:,} |"
        )
    return "\n".join(lines)


def build_report(
    output: Path,
    response_rates: pd.DataFrame,
    thresholds: pd.DataFrame,
    frontier: pd.DataFrame,
    duplicate_count: int,
    non_item_columns: list[str],
) -> None:
    strict_zero = first_at_or_below(frontier, "complete_n", 0)
    strict_one = first_at_or_below(frontier, "complete_n", 1)
    max_row = response_rates.sort_values(["recorded_n", "canonical_order"], ascending=[False, True]).iloc[0]
    min_row = response_rates.sort_values(["recorded_n", "canonical_order"], ascending=[True, True]).iloc[0]
    marginal_50 = int(
        thresholds.loc[thresholds.coverage_threshold_pct == 50, "items_meeting_threshold"].iloc[0]
    )
    sizes = informative_sizes(frontier)
    report = f"""# SAPA item-coverage frontier for Track 1

## Scope and result

This descriptive AA-12 analysis measures raw response availability in the SAPA V5 behavioral-item matrix before any respondent filter, item panel, common feature space, clustering, imputation, construct scoring, or human/model match is chosen. The primary result is a **greedy nested coverage frontier**, not a mathematically proven global Pareto frontier. Threshold selection is deferred to the user.

The release contains {EXPECTED_RESPONDENTS:,} respondent rows and all {EXPECTED_ITEMS} canonical behavioral items. Every respondent ID is unique ({duplicate_count} duplicates), so no rows were deduplicated. The most-observed item is `{max_row.item_id}` with {int(max_row.recorded_n):,} responses ({max_row.recorded_pct_total:.3f}%); the least-observed is `{min_row.item_id}` with {int(min_row.recorded_n):,} ({min_row.recorded_pct_total:.3f}%). Consequently, {marginal_50} items reach 50% marginal coverage. This low marginal coverage is expected under SAPA's random-subset administration and is not ordinary item nonresponse.

## Data-integrity audit

- Source: Harvard Dataverse SAPA V5, *Selected personality data from the SAPA-Project: 08Dec2013 to 26Jul2014*, DOI `10.7910/DVN/SD7SVE`, CC0 1.0.
- Respondent matrix: `{RAW_TAB_NAME}`; SHA256 is recorded in `source_manifest.json`. Raw respondent data remain gitignored and are not copied into this output.
- Canonical dictionary: `research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv`, cross-checked against raw `ItemInfo696.csv`.
- Dimensions: {EXPECTED_RESPONDENTS:,} rows × 719 columns: {EXPECTED_ITEMS} canonical `q_*` behavioral items and {len(non_item_columns)} excluded respondent-ID/demographic/derived fields.
- Response coding: the only nonmissing behavioral-item values are integers 1–6 (`1=Very Inaccurate`, `6=Very Accurate`).
- Missing coding: in the raw behavioral-item cells, missing values are empty tab fields. No literal `NA` occurs in the 696-item matrix. Empty fields alone count as missing; all 1–6 answers count as recorded.
- Duplicate handling: RID was loaded only for a uniqueness count, then discarded. There are {duplicate_count} duplicate RIDs, so no rows were removed or combined.
- Structural availability: SAPA used planned random-subset item administration. The release provides no cell-level planned-versus-unplanned flag, so those mechanisms cannot be separated. All 696 item columns exist, but individual respondents see only subsets.
- Waves/forms: this is one dated V5 extract and has no wave or form indicator. No wave/form split or adjustment was applied.
- Demographics excluded: `{', '.join(non_item_columns)}` were excluded from item eligibility and coverage calculations.

## 1. Marginal item coverage

Marginal coverage counts each item separately. It does **not** establish that the same respondents answered other items at the same marginal threshold. In particular, an item with 90% coverage would not imply that 90% of respondents share complete profiles across all such items.

| Marginal threshold | Items meeting threshold | Share of 696 items |
|---:|---:|---:|
"""
    for row in thresholds.itertuples(index=False):
        report += (
            f"| {row.coverage_threshold_pct:g}% | {row.items_meeting_threshold:,} | "
            f"{row.pct_of_696_items:.3f}% |\n"
        )
    report += f"""

Full item-level counts and percentages are in `sapa_item_response_rates.csv`; the threshold summary is in `sapa_marginal_coverage_thresholds.csv`.

## 2. Joint / nested profile coverage

The sequence starts with the item having the largest marginal response count. At each step it adds the remaining item that maximizes the number of respondents answering **every** item in the expanded panel. Exact ties are resolved by (1) higher marginal response count and (2) earlier position in the canonical 696-item dictionary. Item wording, scale membership, construct names, and psychological content never enter selection.

The relaxed ≥95%, ≥90%, and ≥80% curves are evaluated on the **same nested item order**. For panel size `k`, the required number answered is `ceil(level × k)`. These are descriptive recovery curves only; respondents below 100% are not treated as complete and no value is imputed.

The strict curve has a visually clear, very steep early bend: 6,096 respondents remain at one item, 1,455 at two, 358 at three, 103 at four, and 41 at five. This describes the coverage geometry; it does not nominate any one of those panel sizes. Once the greedy strict cohort becomes tiny, the algorithm can preserve an idiosyncratic respondent for a long tail (one strict-complete respondent from panel sizes 137 through 294). That tail is algorithmically valid but is not evidence of a broadly usable cohort. Relaxed counts can rise at occasional steps because `ceil(level × k)` does not increase at every step while a newly added answered item can move respondents across the fixed integer requirement.

{markdown_table(frontier, sizes)}

The strict frontier first reaches one or fewer complete respondents at panel size {strict_one if strict_one is not None else 'not reached'} and zero at panel size {strict_zero if strict_zero is not None else 'not reached'}. The full 696-step sequence is preserved in `sapa_nested_coverage_frontier.csv`, with the exact availability-only item order in `sapa_nested_item_order.csv`.

## Visual interpretation

`sapa_coverage_frontier.png` shows the full sequence and an early-panel symlog detail. Sharp changes in slope are descriptive coverage tradeoffs, not psychological findings and not a threshold recommendation. Any visually apparent bend should be treated as a region for later scientific consideration; AA-12 deliberately does not select an elbow, panel size, respondent cohort, complete-case rule, or partial-profile method.

## Epistemic status and boundaries

Observed here: raw SAPA availability, marginal item response rates, the deterministic greedy nested item order, strict joint complete-case counts, and relaxed coverage counts. Interpretation is limited to possible regions of sharper coverage loss. Unknowns include the eventual panel size, respondent cohort, partial-profile method, human/model common features, and whether any later human grouping corresponds to model personas.

No construct scores (including the 126 named psychological constructs), imputation, PCA, IRT, FIML, matrix completion, clustering, human/model matching, model PCA, specificity analysis, model inference, activation extraction, external model API, GPU, or RunPod were used. Track 1 remains active; Tracks 2 and 3 remain parked. The next decision is to inspect this frontier and decide what dimensionality/sample-size region is scientifically worth considering—not to begin clustering.
"""
    (output / "sapa_item_coverage_frontier_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--raw-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    raw_dir = args.raw_dir.resolve()
    output = repo / OUTPUT_REL
    output.mkdir(parents=True, exist_ok=True)
    dictionary_path = repo / DICTIONARY_REL
    tab_path = raw_dir / RAW_TAB_NAME
    item_info_path = raw_dir / RAW_ITEM_INFO_NAME
    for required in (dictionary_path, tab_path, item_info_path):
        if not required.is_file():
            raise FileNotFoundError(required)

    dictionary = pd.read_csv(dictionary_path, dtype=str, keep_default_na=False)
    if len(dictionary) != dictionary.item_id.nunique() or len(dictionary) != EXPECTED_ITEMS:
        raise ValueError("Canonical dictionary must contain 696 unique item IDs")
    item_ids = dictionary.item_id.tolist()

    item_info = pd.read_csv(item_info_path, encoding="latin-1", dtype=str, keep_default_na=False)
    raw_info_ids = item_info["Unnamed: 0"].tolist()
    if raw_info_ids != item_ids:
        raise ValueError("Committed canonical dictionary order differs from raw ItemInfo696.csv")
    if item_info["Item"].tolist() != dictionary.item_text.tolist():
        raise ValueError("Committed canonical dictionary wording differs from raw ItemInfo696.csv")

    header = pd.read_csv(tab_path, sep="\t", nrows=0).columns.tolist()
    raw_item_ids = [name for name in header if name.startswith("q_")]
    non_item_columns = [name for name in header if not name.startswith("q_")]
    if raw_item_ids != item_ids:
        raise ValueError("Respondent-data behavioral items differ from canonical dictionary")
    if "RID" not in non_item_columns:
        raise ValueError("RID is required for the duplicate audit")

    loaded = pd.read_csv(
        tab_path,
        sep="\t",
        usecols=["RID", *item_ids],
        dtype=str,
        keep_default_na=False,
        low_memory=False,
    )
    if len(loaded) != EXPECTED_RESPONDENTS:
        raise ValueError(f"Expected {EXPECTED_RESPONDENTS} rows, observed {len(loaded)}")
    duplicate_count = int(loaded.RID.duplicated().sum())
    if duplicate_count:
        raise ValueError(f"Duplicate RIDs found ({duplicate_count}); no silent deduplication allowed")
    responses = loaded[item_ids]
    del loaded
    observed_codes = sorted(pd.unique(responses.to_numpy().ravel()).tolist())
    allowed = ["", *VALID_RESPONSE_CODES]
    if observed_codes != allowed:
        raise ValueError(f"Unexpected item-response codes: {observed_codes}")
    available = responses.to_numpy() != ""
    del responses

    marginal_n = available.sum(axis=0).astype(int)
    rate_rows = []
    marginal_order = sorted(range(EXPECTED_ITEMS), key=lambda j: (-int(marginal_n[j]), j))
    ranks = {j: rank for rank, j in enumerate(marginal_order, 1)}
    for j, item in dictionary.iterrows():
        rate_rows.append(
            {
                "canonical_order": j + 1,
                "marginal_coverage_rank": ranks[j],
                "item_id": item.item_id,
                "item_text": item.item_text,
                "recorded_n": int(marginal_n[j]),
                "recorded_pct_total": pct(int(marginal_n[j]), EXPECTED_RESPONDENTS),
                "missing_n": EXPECTED_RESPONDENTS - int(marginal_n[j]),
                "missing_pct_total": pct(EXPECTED_RESPONDENTS - int(marginal_n[j]), EXPECTED_RESPONDENTS),
            }
        )
    response_rates = pd.DataFrame(rate_rows)
    # The prior canonical dictionary already contains independently generated N values.
    if response_rates.recorded_n.tolist() != dictionary.valid_response_n.astype(int).tolist():
        raise AssertionError("Recomputed item counts disagree with canonical dictionary")

    thresholds = threshold_rows(marginal_n, EXPECTED_RESPONDENTS)
    order, strict_counts, tie_counts = greedy_nested_order(available, marginal_n)
    frontier = build_frontier(available, order, strict_counts)
    frontier["added_item_id"] = [item_ids[j] for j in order]
    order_rows = []
    for step, j in enumerate(order, 1):
        order_rows.append(
            {
                "selection_step": step,
                "item_id": item_ids[j],
                "item_text": dictionary.iloc[j].item_text,
                "canonical_order": j + 1,
                "marginal_recorded_n": int(marginal_n[j]),
                "marginal_recorded_pct_total": pct(int(marginal_n[j]), EXPECTED_RESPONDENTS),
                "expanded_panel_complete_n": strict_counts[step - 1],
                "final_tie_count_after_joint_and_marginal_rules": tie_counts[step - 1],
            }
        )
    item_order = pd.DataFrame(order_rows)

    response_rates.to_csv(output / "sapa_item_response_rates.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    thresholds.to_csv(output / "sapa_marginal_coverage_thresholds.csv", index=False)
    frontier.to_csv(output / "sapa_nested_coverage_frontier.csv", index=False)
    item_order.to_csv(output / "sapa_nested_item_order.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    render_figure(frontier, output)
    build_report(output, response_rates, thresholds, frontier, duplicate_count, non_item_columns)

    source_manifest = {
        "artifact": "AA-12 SAPA item-coverage frontier",
        "generated_at": utc_now(),
        "analysis_model": "GPT-5.5",
        "branch": git(repo, "branch", "--show-current"),
        "generation_base_commit": git(repo, "rev-parse", "HEAD"),
        "source": {
            "dataset": "Selected personality data from the SAPA-Project: 08Dec2013 to 26Jul2014",
            "release_version": "5.0",
            "doi": "10.7910/DVN/SD7SVE",
            "license": "CC0 1.0",
            "respondent_tab_logical_name": RAW_TAB_NAME,
            "respondent_tab_sha256": sha256(tab_path),
            "raw_item_info_logical_name": RAW_ITEM_INFO_NAME,
            "raw_item_info_sha256": sha256(item_info_path),
            "canonical_dictionary_path": str(DICTIONARY_REL),
            "canonical_dictionary_sha256": sha256(dictionary_path),
        },
        "integrity": {
            "respondent_rows": EXPECTED_RESPONDENTS,
            "total_columns": len(header),
            "canonical_behavioral_items_expected": EXPECTED_ITEMS,
            "canonical_behavioral_items_present": len(raw_item_ids),
            "excluded_nonbehavioral_columns": non_item_columns,
            "duplicate_rids": duplicate_count,
            "observed_behavioral_response_codes": observed_codes,
            "missing_behavioral_cell_encoding": "empty tab field",
            "literal_NA_behavioral_cells": 0,
            "planned_missingness": True,
            "cell_level_planned_missingness_indicator_available": False,
            "wave_or_form_indicator_available": False,
        },
        "method": {
            "item_eligibility": "exact 696 item IDs and order in the canonical committed dictionary, cross-checked with raw ItemInfo696.csv and respondent q_* columns",
            "greedy_objective": "maximize expanded-panel respondents answering 100% of selected items",
            "tie_breaks": ["higher marginal response count", "earlier canonical dictionary order"],
            "frontier_status": "greedy nested frontier; not a proven global Pareto optimum",
            "relaxed_levels": [0.95, 0.90, 0.80],
            "relaxed_rule": "answered count >= ceil(level * panel size) on the same nested panel",
            "random_seed": None,
        },
        "privacy": {
            "respondent_level_output_written": False,
            "respondent_ids_written": False,
            "individual_response_masks_written": False,
            "aggregate_outputs_only": True,
        },
        "prohibited_methods": {
            "imputation": False,
            "construct_scoring": False,
            "clustering": False,
            "human_model_matching": False,
            "human_pca_or_projection": False,
            "model_inference": False,
            "activation_extraction": False,
            "external_model_api": False,
            "gpu_or_runpod": False,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "command": f"python {OUTPUT_REL / Path(__file__).name} --repo-root . --raw-dir <gitignored-sapa-v5-directory>",
    }
    (output / "source_manifest.json").write_text(
        json.dumps(source_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
