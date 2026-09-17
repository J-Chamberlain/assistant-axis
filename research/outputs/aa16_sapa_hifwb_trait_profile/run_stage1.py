#!/usr/bin/env python3
"""AA-16 Stage 1: existing SAPA bridge to 240-trait HiFWB profiles.

CPU only. Reads raw SAPA responses in memory; exports aggregate tables only.
No model PC coordinate, activation, persona, or viewer input is used.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import platform
from collections import Counter, defaultdict
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RESEARCH = ROOT / "research/outputs"
BRIDGE = RESEARCH / "human_trait_dataset_feasibility/sapa_review/sapa_trait_bridge_provisional_v1.csv"
CANDIDATES = RESEARCH / "human_trait_dataset_feasibility/sapa/sapa_model_trait_candidate_crosswalk.csv"
SUPPORT = RESEARCH / "sapa_bridge_psychometric_audit/sapa_trait_bridge_psychometric_support_v1.csv"
ORIENTATION_SOURCE = RESEARCH / "sapa_bridge_psychometric_audit/run_sapa_bridge_psychometric_audit.py"
TRAITS = RESEARCH / "three_model_trait_pca/trait_pc_scores_all.csv"
HIFWB = RESEARCH / "sapa_hifwb_reproducibility/wellbeing_item_freeze.csv"
RAW_NAME = "sapaTempData696items08dec2013thru26jul2014.tab"
RAW_SHA = "fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6"
HIFWB_SHA = "dcac8f8d2e82c6fa337a8c34472b8b1901d7c709823618dd4bf614ed885a46e0"
SCHEMA_SHA = "787f539747deee8da85bc64da9c3407eaf741f6da9277dcbec7ec79b2a40260c"
BRIDGE_SHA = "e70be82752ec8ec4a7a8c64c7f5d37386b0997363c16a721e59a6aa0ac254e22"
MIN_ASSOC_N = 30
Z95 = NormalDist().inv_cdf(.975)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def save_csv(name: str, data: list[dict]) -> None:
    assert data, name
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, list(data[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def split(value: str) -> list[str]:
    return [part for part in value.split(";") if part]


def frozen_reversals() -> dict[str, set[str]]:
    tree = ast.parse(ORIENTATION_SOURCE.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "REVERSE_BY_TRAIT" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("Prior frozen REVERSE_BY_TRAIT definition not found")


def trait_vocabulary() -> list[str]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows(TRAITS):
        grouped[row["model"]].append(row["trait"])
    assert set(grouped) == {"qwen", "llama", "gemma"}
    assert all(len(grouped[m]) == len(set(grouped[m])) == 240 for m in grouped)
    assert grouped["qwen"] == grouped["llama"] == grouped["gemma"]
    return grouped["qwen"]


def bridge_audit(vocab: list[str], outcomes: list[dict]) -> tuple[list[dict], list[dict], list[dict], dict]:
    candidate = {r["model_trait"]: r for r in rows(CANDIDATES)}
    bridge = {r["trait"]: r for r in rows(BRIDGE)}
    support = {r["trait"]: r for r in rows(SUPPORT)}
    assert len(candidate) == 240 and len(bridge) == len(support) == 74
    assert set(candidate) == set(vocab) and set(bridge) == set(support)
    assert sha(BRIDGE) == BRIDGE_SHA
    assert Counter(r["bridge_tier"] for r in bridge.values()) == {"primary_direct": 45, "secondary_close": 29}
    direct_ids = {r["item_id"] for r in outcomes}
    reversals = frozen_reversals()
    item_sets: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for trait, row in bridge.items():
        item_ids = split(row["sapa_item_ids"])
        assert item_ids and len(item_ids) == len(set(item_ids))
        assert reversals.get(trait, set()) <= set(item_ids)
        item_sets[tuple(sorted(item_ids))].append(trait)
    duplicate_rows = []
    for item_set, names in sorted(item_sets.items()):
        if len(names) < 2:
            continue
        names = sorted(names)
        signs = {n: [(-1 if item in reversals.get(n, set()) else 1) for item in item_set] for n in names}
        inverse = len(names) == 2 and all(a == -b for a, b in zip(signs[names[0]], signs[names[1]]))
        duplicate_rows.append({"duplicate_group": hashlib.sha256(";".join(item_set).encode()).hexdigest()[:12],
                               "item_set": ";".join(item_set), "trait_count": len(names),
                               "model_trait_labels": ";".join(names), "inverse_keyed_alias": int(inverse),
                               "direct_count": sum(bridge[n]["bridge_tier"] == "primary_direct" for n in names),
                               "close_count": sum(bridge[n]["bridge_tier"] == "secondary_close" for n in names)})
    audit = []
    for trait in vocab:
        candidate_row = candidate[trait]
        b = bridge.get(trait)
        ids = split(b["sapa_item_ids"]) if b else []
        scales = split(b["source_scales"]) if b else []
        same_source = item_sets[tuple(sorted(ids))] if b else []
        shared_items = sorted(set(ids) & direct_ids)
        other_item_reuse = sorted(n for n, other in bridge.items() if n != trait and set(ids) & set(split(other["sapa_item_ids"]))) if b else []
        other_scale_reuse = sorted(n for n, other in bridge.items() if n != trait and set(scales) & set(split(other["source_scales"]))) if b else []
        tier = "direct" if b and b["bridge_tier"] == "primary_direct" else "close" if b else "absent"
        row = {"model_trait": trait, "model_trait_description": candidate_row["canonical_definition"],
               "sapa_proxy_construct": trait if b else "", "sapa_source_scales": b["source_scales"] if b else "",
               "sapa_item_ids": b["sapa_item_ids"] if b else "", "sapa_item_wording": b["sapa_exact_wording"] if b else "",
               "mapping_tier": tier, "mapping_decision": b["review_decision"] if b else "",
               "mapping_provenance": "frozen_45_29_provisional_bridge_v1" if b else "no_retained_bridge",
               "prior_45_direct_audit": int(tier == "direct"), "prior_74_direct_close_audit": int(bool(b)),
               "original_feasibility_category": candidate_row["coverage_category"],
               "original_feasibility_status": candidate_row["coverage_label"],
               "human_measurement_support_tier": support[trait]["human_measurement_support_tier"] if b else "",
               "predictor_reverse_item_ids": ";".join(sorted(reversals.get(trait, set()))) if b else "",
               "predictor_item_count": len(ids), "exact_source_group": hashlib.sha256(";".join(sorted(ids)).encode()).hexdigest()[:12] if b else "",
               "exact_source_group_size": len(same_source),
               "exact_source_other_labels": ";".join(sorted(set(same_source) - {trait})),
               "partial_item_reuse_other_labels": ";".join(other_item_reuse),
               "shared_scale_other_labels": ";".join(other_scale_reuse),
               "overlap_with_hifwb_item_ids": ";".join(shared_items),
               "primary_composite_eligible_mapping": int(tier == "direct" and not shared_items)}
        audit.append(row)
    assert len(audit) == 240 and Counter(r["mapping_tier"] for r in audit) == {"direct": 45, "close": 29, "absent": 166}
    return audit, duplicate_rows, list(bridge.values()), reversals


def standardized_item_matrix(tab: Path, item_ids: list[str]) -> tuple[dict[str, np.ndarray], dict]:
    with tab.open(newline="") as stream:
        header = next(csv.reader(stream, delimiter="\t"))
    assert len(header) == 719 and len(set(header)) == 719
    schema = hashlib.sha256("\x1f".join(header).encode()).hexdigest()
    assert schema == SCHEMA_SHA and set(item_ids) <= set(header)
    frame = pd.read_csv(tab, sep="\t", usecols=item_ids, na_values=["NA"], low_memory=False)
    assert frame.shape == (23679, len(item_ids))
    frame = frame.apply(pd.to_numeric, errors="coerce")
    matrix = frame.to_numpy(dtype=np.float64)
    means = np.nanmean(matrix, axis=0)
    sds = np.nanstd(matrix, axis=0, ddof=1)
    assert np.all(np.isfinite(means)) and np.all(np.isfinite(sds) & (sds > 0))
    z = (matrix - means) / sds
    return {item: z[:, i] for i, item in enumerate(frame.columns)}, {
        "rows": int(len(frame)), "columns": len(header), "schema_fingerprint_full_header": schema,
        "read_item_count": len(item_ids), "source_sha256": sha(tab), "source_bytes": tab.stat().st_size,
        "observed_read_cells": int(np.isfinite(matrix).sum())}


def score_mean(z: dict[str, np.ndarray], item_ids: list[str], negative: set[str], minimum: int) -> tuple[np.ndarray, np.ndarray]:
    values = np.column_stack([(-z[item] if item in negative else z[item]) for item in item_ids])
    count = np.isfinite(values).sum(axis=1)
    result = np.full(len(count), np.nan)
    np.divide(np.nansum(values, axis=1), count, out=result, where=count >= minimum)
    return result, count


def correlation(x: np.ndarray, y: np.ndarray, rank: bool = False) -> tuple[float, float, float]:
    if rank:
        x = pd.Series(x).rank(method="average").to_numpy(dtype=float)
        y = pd.Series(y).rank(method="average").to_numpy(dtype=float)
    if np.std(x, ddof=1) <= 1e-12 or np.std(y, ddof=1) <= 1e-12:
        return float("nan"), float("nan"), float("nan")
    r = float(np.corrcoef(x, y)[0, 1])
    if not np.isfinite(r):
        return float("nan"), float("nan"), float("nan")
    fisher = math.atanh(float(np.clip(r, -1 + 1e-12, 1 - 1e-12)))
    width = Z95 / math.sqrt(len(x) - 3)
    return r, math.tanh(fisher - width), math.tanh(fisher + width)


def association_rows(audit: list[dict], outcomes: list[dict], z: dict[str, np.ndarray], reversals: dict[str, set[str]]) -> tuple[list[dict], list[dict], list[dict], dict]:
    direct_ids = [r["item_id"] for r in outcomes]
    negative_outcomes = {r["item_id"] for r in outcomes if r["orientation"] == "-"}
    assert len(direct_ids) == 13 and len(negative_outcomes) == 6
    outcome_scores: dict[str, np.ndarray] = {}
    for item in direct_ids:
        outcome_scores[item] = -z[item] if item in negative_outcomes else z[item]
    composite, composite_n = score_mean(z, direct_ids, negative_outcomes, 2)
    outcome_scores["HiFWB_composite"] = composite
    outcome_ids = ["HiFWB_composite", *direct_ids]
    assert int(np.isfinite(composite).sum()) == 8664, "AA-13 frozen composite eligibility was not reproduced"
    target = {r["item_id"]: r for r in outcomes}
    by_trait = {}
    for row in audit:
        if row["mapping_tier"] == "absent":
            continue
        ids = split(row["sapa_item_ids"])
        minimum = min(2, len(ids))
        by_trait[row["model_trait"]] = score_mean(z, ids, reversals.get(row["model_trait"], set()), minimum)
    long_rows, association_table, overlap_audit = [], [], []
    for row in audit:
        name = row["model_trait"]
        item_set = set(split(row["sapa_item_ids"]))
        for outcome_id in outcome_ids:
            overlap = sorted(item_set & (set(direct_ids) if outcome_id == "HiFWB_composite" else {outcome_id}))
            descriptor = "frozen_13_item_composite" if outcome_id == "HiFWB_composite" else target[outcome_id]["text"]
            record = {
                "model_trait": name, "model_trait_description": row["model_trait_description"],
                "outcome_id": outcome_id, "outcome_description": descriptor,
                "outcome_content": "Composite" if outcome_id == "HiFWB_composite" else target[outcome_id]["content"],
                "mapping_tier": row["mapping_tier"], "sapa_proxy_construct": row["sapa_proxy_construct"],
                "sapa_source_scales": row["sapa_source_scales"], "sapa_item_ids": row["sapa_item_ids"],
                "human_measurement_support_tier": row["human_measurement_support_tier"],
                "exact_source_group": row["exact_source_group"],
                "exact_source_group_size": row["exact_source_group_size"],
                "overlap_item_ids": ";".join(overlap), "predictor_min_observed_items": min(2, len(item_set)) if item_set else "",
                "outcome_min_observed_items": 2 if outcome_id == "HiFWB_composite" else 1,
                "eligible_respondent_n": "", "pearson_r": "", "pearson_ci95_low": "", "pearson_ci95_high": "",
                "spearman_r": "", "spearman_ci95_approx_low": "", "spearman_ci95_approx_high": "",
                "association_status": "", "unavailable_reason": ""}
            if name not in by_trait:
                record["association_status"] = "unavailable"
                record["unavailable_reason"] = "no_retained_sapa_bridge"
            else:
                predictor, _ = by_trait[name]
                outcome = outcome_scores[outcome_id]
                eligible = np.isfinite(predictor) & np.isfinite(outcome)
                n = int(eligible.sum())
                record["eligible_respondent_n"] = n
                if overlap:
                    record["association_status"] = "unavailable"
                    record["unavailable_reason"] = "predictor_outcome_item_overlap"
                elif n < MIN_ASSOC_N:
                    record["association_status"] = "unavailable"
                    record["unavailable_reason"] = "eligible_n_below_30"
                else:
                    pearson = correlation(predictor[eligible], outcome[eligible])
                    spearman = correlation(predictor[eligible], outcome[eligible], rank=True)
                    if not all(np.isfinite(v) for v in (*pearson, *spearman)):
                        record["association_status"] = "unavailable"
                        record["unavailable_reason"] = "constant_or_nonfinite_score"
                    else:
                        record.update({"pearson_r": round(pearson[0], 8),
                                       "pearson_ci95_low": round(pearson[1], 8),
                                       "pearson_ci95_high": round(pearson[2], 8),
                                       "spearman_r": round(spearman[0], 8),
                                       "spearman_ci95_approx_low": round(spearman[1], 8),
                                       "spearman_ci95_approx_high": round(spearman[2], 8),
                                       "association_status": "observed"})
                overlap_audit.append({"model_trait": name, "outcome_id": outcome_id,
                                      "mapping_tier": row["mapping_tier"],
                                      "predictor_item_ids": row["sapa_item_ids"],
                                      "overlap_item_ids": ";".join(overlap), "overlap": int(bool(overlap)),
                                      "eligible_respondent_n_before_overlap_exclusion": n,
                                      "primary_estimate_excluded": int(bool(overlap)),
                                      "exact_source_group": row["exact_source_group"]})
                association_table.append(record.copy())
            long_rows.append(record)
    assert len(long_rows) == 240 * 14 and len(association_table) == len(overlap_audit) == 74 * 14
    assert all(r["pearson_r"] == "" for r in long_rows if r["mapping_tier"] == "absent" or r["overlap_item_ids"])
    return long_rows, association_table, overlap_audit, {
        "composite_eligible_n": int(np.isfinite(composite).sum()),
        "composite_observed_item_count_min": int(composite_n[np.isfinite(composite)].min()),
        "direct_outcome_ids": direct_ids,
        "reverse_keyed_direct_ids": sorted(negative_outcomes),
    }


def summarize(audit: list[dict], long_rows: list[dict]) -> list[dict]:
    summary = []
    outcome_ids = list(dict.fromkeys(r["outcome_id"] for r in long_rows))
    assert len(outcome_ids) == 14
    for outcome_id in outcome_ids:
        subset = [r for r in long_rows if r["outcome_id"] == outcome_id]
        assert len(subset) == 240
        for tier in ("direct", "close", "absent"):
            group = [r for r in subset if r["mapping_tier"] == tier]
            observed = [r for r in group if r["association_status"] == "observed"]
            summary.append({"outcome_id": outcome_id, "mapping_tier": tier,
                            "model_trait_labels": len(group), "observed_associations": len(observed),
                            "unique_observed_item_set_constructs": len({r["exact_source_group"] for r in observed}),
                            "overlap_excluded": sum(r["unavailable_reason"] == "predictor_outcome_item_overlap" for r in group),
                            "low_n_unavailable": sum(r["unavailable_reason"] == "eligible_n_below_30" for r in group),
                            "unmatched_unavailable": sum(r["unavailable_reason"] == "no_retained_sapa_bridge" for r in group),
                            "median_observed_respondent_n": round(float(np.median([int(r["eligible_respondent_n"]) for r in observed])), 2) if observed else ""})
    assert len(summary) == 14 * 3
    return summary


def indicator_similarity(long_rows: list[dict]) -> list[dict]:
    """Descriptive profile concordance on unique direct human item sets."""
    profiles = {}
    for outcome in dict.fromkeys(r["outcome_id"] for r in long_rows):
        if outcome == "HiFWB_composite":
            continue
        grouped = defaultdict(list)
        for row in long_rows:
            if row["outcome_id"] == outcome and row["mapping_tier"] == "direct" and row["association_status"] == "observed":
                grouped[row["exact_source_group"]].append(float(row["pearson_r"]))
        profiles[outcome] = {key: float(np.mean(values)) for key, values in grouped.items()}
    result = []
    keys = list(profiles)
    for i, left in enumerate(keys):
        for right in keys[i + 1:]:
            common = sorted(set(profiles[left]) & set(profiles[right]))
            result.append({"indicator_a": left, "indicator_b": right, "unique_direct_constructs": len(common),
                           "association_profile_r": round(float(np.corrcoef(
                               [profiles[left][x] for x in common], [profiles[right][x] for x in common])[0, 1]), 8)
                           if len(common) >= 3 else ""})
    assert len(result) == 78
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True, help="Uncommitted directory holding frozen external SAPA .tab")
    args = parser.parse_args()
    tab = args.data_dir / RAW_NAME
    assert tab.is_file() and sha(tab) == RAW_SHA
    assert sha(HIFWB) == HIFWB_SHA
    outcomes = [r for r in rows(HIFWB) if r["tier"] == "DIRECT"]
    assert len(outcomes) == 13 and len({r["item_id"] for r in outcomes}) == 13
    vocab = trait_vocabulary()
    audit, duplicate_rows, _, reversals = bridge_audit(vocab, outcomes)
    item_ids = sorted(set(r["item_id"] for r in outcomes) |
                      {item for row in audit for item in split(row["sapa_item_ids"])})
    z, source = standardized_item_matrix(tab, item_ids)
    long_rows, associations, overlap, scoring = association_rows(audit, outcomes, z, reversals)
    summary = summarize(audit, long_rows)
    composite = [r for r in long_rows if r["outcome_id"] == "HiFWB_composite"]
    similarity = indicator_similarity(long_rows)
    save_csv("existing_trait_bridge_audit.csv", audit)
    save_csv("duplicate_mapping_groups.csv", duplicate_rows)
    save_csv("hifwb_trait_profile_240_long.csv", long_rows)
    save_csv("hifwb_trait_profile_240_composite.csv", composite)
    save_csv("hifwb_indicator_trait_associations.csv", associations)
    save_csv("outcome_overlap_audit.csv", overlap)
    save_csv("coverage_summary.csv", summary)
    save_csv("indicator_profile_similarity.csv", similarity)

    comp_observed = [r for r in composite if r["association_status"] == "observed"]
    comp_direct = [r for r in comp_observed if r["mapping_tier"] == "direct"]
    positives = sorted(comp_direct, key=lambda r: float(r["pearson_r"]), reverse=True)[:8]
    negatives = sorted(comp_direct, key=lambda r: float(r["pearson_r"]))[:8]
    duplicate_labels = sum(int(r["trait_count"]) for r in duplicate_rows)
    overlap_composite = [r for r in composite if r["unavailable_reason"] == "predictor_outcome_item_overlap"]
    assert len(composite) == 240 and len(comp_observed) == 69 and len(overlap_composite) == 5
    assert sum(r["association_status"] == "observed" for r in long_rows) == 1026
    assert sum(r["association_status"] == "unavailable" for r in long_rows) == 240 * 14 - 1026
    assert all(r["pearson_r"] == "" for r in long_rows if r["association_status"] != "observed")
    assert all(not r["overlap_item_ids"] for r in long_rows if r["association_status"] == "observed")
    assert len({r["model_trait"] for r in composite}) == 240
    assert len(set(r["outcome_id"] for r in long_rows)) == 14
    assert duplicate_labels == 8
    assert source["rows"] == 23679 and source["columns"] == 719
    assert source["source_sha256"] == RAW_SHA
    assert scoring["composite_eligible_n"] == 8664

    verification = {
        "stage": "AA-16 Stage 1 only", "status": "passed", "cpu_only": True,
        "model_inference_run": False, "paid_compute_cost_usd": 0,
        "trait_pc_projection_run": False, "viewer_modified": False, "persona_scoring_run": False,
        "sources": {"hifwb_sha256": sha(HIFWB), "sapa_matrix": source,
                    "frozen_bridge_sha256": sha(BRIDGE), "candidate_crosswalk_sha256": sha(CANDIDATES),
                    "psychometric_support_sha256": sha(SUPPORT), "reverse_keying_source_sha256": sha(ORIENTATION_SOURCE)},
        "software": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
        "scoring": scoring,
        "checks": {"shared_trait_labels": 240, "direct_bridge_labels": 45, "close_bridge_labels": 29,
                   "unmatched_labels": 166, "outcomes": 14, "long_rows": len(long_rows),
                   "composite_rows": len(composite), "matched_outcome_rows": len(associations),
                   "observed_outcome_rows": 1026, "overlap_excluded_outcome_rows": sum(bool(r["overlap_item_ids"]) for r in long_rows),
                   "composite_observed_labels": len(comp_observed),
                   "composite_observed_unique_item_sets": len({r["exact_source_group"] for r in comp_observed}),
                   "composite_overlap_excluded_labels": len(overlap_composite),
                   "duplicate_exact_item_set_groups": len(duplicate_rows), "duplicate_labels": duplicate_labels,
                   "no_estimate_for_unavailable": True, "no_overlapping_primary_estimate": True,
                   "no_respondent_rows_written": True},
        "schema_fingerprint_note": "The earlier 63-character fingerprint is a transcription error; the recomputed full 719-column header SHA256 has the additional 7 before dcbec7."
    }
    (OUT / "stage1_verification_report.json").write_text(json.dumps(verification, indent=2) + "\n")

    def listing(data: list[dict]) -> str:
        return "\n".join(f"- {r['model_trait']}: r = {float(r['pearson_r']):+.3f}, N = {r['eligible_respondent_n']} ({r['human_measurement_support_tier']})" for r in data)

    by_outcome = []
    for outcome in outcomes:
        result = [r for r in long_rows if r["outcome_id"] == outcome["item_id"] and r["mapping_tier"] == "direct" and r["association_status"] == "observed"]
        pos = max(result, key=lambda r: float(r["pearson_r"]))
        neg = min(result, key=lambda r: float(r["pearson_r"]))
        by_outcome.append(f"| {outcome['item_id']} | {outcome['content']} | {len(result)} | {pos['model_trait']} ({float(pos['pearson_r']):+.3f}) | {neg['model_trait']} ({float(neg['pearson_r']):+.3f}) |")
    pair_sorted = sorted(similarity, key=lambda r: float(r["association_profile_r"]))
    findings = f"""# AA-16 Stage 1 findings: frozen HiFWB association profile\n\nObserved: The frozen AA-14 vocabulary has 240 shared labels; the existing human bridge retains 45 direct and 29 close model-label mappings, leaving 166 absent. This is a human association profile over model-trait *names*, not a model activation or PC analysis. The 74 retained labels represent 70 exact predictor-item sets before outcome-overlap exclusions.\n\nObserved: The composite has {len(comp_direct)} direct and {len(comp_observed)} direct-plus-close observed label associations, representing {len({r['exact_source_group'] for r in comp_observed})} distinct exact item sets. Five mapped labels ({', '.join(r['model_trait'] for r in overlap_composite)}) are withheld for circular predictor/outcome item overlap. The long table has {len(long_rows)} rows (240 traits × 14 outcomes) with explicit blanks for unsupported or excluded associations. Pearson is primary and Spearman is a sensitivity estimate; Fisher-transformed 95% intervals are descriptive and unadjusted.\n\n## Stage 1 questions\n\n1. **Direct support:** 45/240 labels (18.75%) have an established direct bridge before outcome overlap; {len(comp_direct)}/240 have observed nonoverlapping composite associations.\n2. **Direct plus close:** 74/240 labels (30.83%) have an established bridge; {len(comp_observed)}/240 have observed nonoverlapping composite associations.\n3. **Unmatched:** 166/240 labels (69.17%) have no retained bridge; no value was inferred for them.\n4. **Duplicate mappings:** {len(duplicate_rows)} exact item-set groups involve {duplicate_labels} labels, yielding 70 unique item sets among 74 mappings. These are descriptive duplicate labels, not independent human constructs. Partial item and scale reuse are additionally exposed in the bridge audit.\n5. **Overlap exclusions:** {len(overlap_composite)} labels for the composite; {sum(bool(r['overlap_item_ids']) for r in long_rows)} trait–outcome combinations across the full profile. No excluded combination has an association estimate in the primary table.\n6. **Strongest composite associations:** The following lists use direct, nonoverlapping mappings only. They are descriptive correlations, not causal effects or model-derived scores.\n\nPositive:\n{listing(positives)}\n\nNegative:\n{listing(negatives)}\n\n7. **Indicator-specific profiles:** The table shows directly supported, nonoverlapping coverage and the strongest observed positive/negative trait per indicator; exact rankings and all 240-row profiles are in the CSV. At the unique-item-set level, pairwise indicator profile correlations range from {float(pair_sorted[0]['association_profile_r']):+.3f} ({pair_sorted[0]['indicator_a']} vs {pair_sorted[0]['indicator_b']}) to {float(pair_sorted[-1]['association_profile_r']):+.3f} ({pair_sorted[-1]['indicator_a']} vs {pair_sorted[-1]['indicator_b']}). This descriptive comparison is not evidence for a single wellbeing direction.\n\n| Indicator | Domain | Direct observed labels | Strongest positive | Strongest negative |\n|---|---|---:|---|---|\n{chr(10).join(by_outcome)}\n\n8. **Stage 2 adequacy:** Interpretation: The direct bridge covers fewer than one fifth of the vocabulary, and several bridges have limited psychometric support. A later PC mapping could be exploratory within the supported subset, but these data cannot justify a full 240-trait wellbeing landscape or a stable direction without further coverage and duplicate-aware validation. Stage 2 has not begun.\n\n## Interrupted-work audit\n\nObserved: The existing `codex/aa16-sapa-hifwb-trait-pc-crosswalk` branch was at the clean AA-15 commit `9a8e3c6fae4f320a4909d09dff1b88c6e84ae20b` when Stage 1 resumed: no staged, unstaged, or untracked AA-16 files and no diff from the AA-15 branch. The prior startup audit was reused after confirming its cached manifest hash had not changed. Reusable inputs were the AA-15 provenance repair, AA-14 240-label vocabulary, frozen HiFWB scoring, and prior bridge audits. AA-15 prospective extraction scripts and viewer drafts are useful only for a later, separate direct-representation question; they were not executed or modified. No interrupted AA-16 numerical or viewer output existed to preserve, and no partial result was silently treated as valid.\n\n## Provenance and limitations\n\nObserved: The 13 DIRECT items and positive-wellbeing orientation come from the frozen HiFWB file (SHA256 `{HIFWB_SHA}`). The external SAPA matrix is DOI 10.7910/DVN/SD7SVE, 23,679 × 719, SHA256 `{RAW_SHA}`. The prior schema-fingerprint string is 63 characters (a transcription error); the recomputed full-header SHA256 is `{SCHEMA_SHA}`. This correction does not alter the data or numeric associations. Predictor reverse-keying follows the prior psychometric script, and composite scoring reproduces the AA-13 8,664-respondent eligibility count. Planned missingness is handled pairwise with observed-item minimums, without raw-data imputation.\n\nInterpretation: The correlations are between measured SAPA trait proxies and human HiFWB, then attached to matched model-trait labels. They do not show how any language model encodes wellbeing. The bridge is provisional, overlap exclusions are outcome-specific, duplicate/near-duplicate sources reduce effective independent coverage, and the simple Fisher intervals do not account for scale-construction uncertainty or multiple comparisons.\n\nHypothesis: Distinct affective, self-concept, interpersonal, and vitality items may associate with different subsets of supported traits. Testing this against model trait PCs is a later stage.\n\nAA-15's prospective direct-extraction plan was not run, incurred no cost, is deferred, and is unnecessary for this trait-mediated Stage 1 analysis. Its provenance repair remains intact. No model inference, activation generation, PC projection, viewer change, or persona scoring was performed here.\n"""
    (OUT / "stage1_findings.md").write_text(findings)
    audit_md = f"""# Existing trait bridge audit\n\nObserved: The frozen 240-label AA-14 vocabulary was joined by exact trait label to the prior 240-row feasibility crosswalk and the retained provisional 74-row SAPA bridge (45 direct, 29 close). No new semantic remapping was performed. The bridge records exact SAPA item composition, wording, source scales, and prior psychometric-support tier; the complete 240-row audit is `existing_trait_bridge_audit.csv`. `sapa_proxy_construct` is the prior bridge's working trait-proxy name (not an official SAPA scale score); `sapa_source_scales` lists the actual item-source scales.\n\nAbsent labels ({sum(r['mapping_tier']=='absent' for r in audit)}) have no retained SAPA proxy. The original feasibility category is preserved for context but does not promote an absent label into a direct or close match. No ambiguous candidate was admitted to the primary profile.\n\nObserved: {len(duplicate_rows)} exact item-set groups involve {duplicate_labels} model labels; the secular/spiritual group is reverse-keyed rather than two independent human observations. Exact group IDs are SHA256 prefixes of sorted item IDs, and partial item/scale reuse is separately listed. The composite overlap exclusions are {', '.join(r['model_trait']+' ('+r['overlap_item_ids']+')' for r in overlap_composite)}. Overlap is tested against each outcome separately as well.\n\nThe primary composite profile uses only direct, nonoverlapping mappings; close mappings are retained as a sensitivity tier. Both tiers receive observed association values in the descriptive table, with mapping provenance and eligibility explicit. Multiple model labels tied to the same human item set must be collapsed or weighted in downstream inference. This Stage 1 makes no across-trait inferential test.\n\nThe AA-13 external-matrix schema fingerprint was transcribed as a 63-character string; recomputing SHA256 of the full 719-column header joined with ASCII unit separators gives `{SCHEMA_SHA}`. The raw-file SHA256 and 23,679 × 719 dimensions match the frozen dependency.\n"""
    (OUT / "existing_trait_bridge_audit.md").write_text(audit_md)
    artifact_rows = []
    for path in sorted(OUT.iterdir()):
        if not path.is_file() or path.name == "stage1_artifact_inventory.csv":
            continue
        artifact_rows.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                              "sha256": sha(path), "stage": "AA-16 Stage 1",
                              "raw_url": "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa16-sapa-hifwb-trait-pc-crosswalk/" + str(path.relative_to(ROOT))})
    save_csv("stage1_artifact_inventory.csv", artifact_rows)
    print(json.dumps({"status": "passed", "direct": 45, "close": 29, "absent": 166,
                      "composite_observed": len(comp_observed), "composite_overlap_excluded": len(overlap_composite),
                      "duplicate_groups": len(duplicate_rows), "long_rows": len(long_rows)}, indent=2))


if __name__ == "__main__":
    main()
