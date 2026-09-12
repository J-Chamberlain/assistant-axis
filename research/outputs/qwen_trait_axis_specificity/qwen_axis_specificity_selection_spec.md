# Qwen trait axis-specificity selection specification

Status: frozen before inspecting any axis-specificity result  
Frozen at: 2026-09-12T18:08:06Z  
Source commit: `667acdd634bfb8c39d40432fe60f0c5ef3bbbeeb`  
Model: `Qwen/Qwen3-32B` only  
Supported subspace: PC1-PC6 (PC1-PC3 strict core; PC4-PC6 supported secondary/provisional axes)

## Inputs and invariants

- Reuse the saved 1,440 Pearson/Spearman trait-PC associations from `research/outputs/qwen_trait_family_human_inventory/qwen_trait_pc_correlations_all.csv`; do not recompute them as a new analysis.
- Reuse the original association-family membership exactly: `|Pearson r| >= 0.50`, within-PC Benjamini-Hochberg FDR `q < 0.01`, and prior role-bootstrap sign stability `>= 0.95`.
- Use all six supported PCs in specificity denominators and off-axis comparisons.
- Use the same 275 aligned Qwen role observations only for the new bootstrap and numerical verification. No activation or model inference is permitted.

## Deterministic specificity definitions

For trait `t` and target PC `j`, let `r_j` be its saved Pearson correlation and let `r_k` denote each of the six saved correlations.

- `target_abs_r = |r_j|`
- `max_off_axis_abs_r = max_{k != j} |r_k|`
- `second_best_pc` is the off-axis PC attaining that maximum; exact ties are broken by lower PC number.
- `dominance_gap = |r_j| - max_off_axis_abs_r`
- `dominance_ratio = |r_j| / max(max_off_axis_abs_r, 1e-12)`
- `six_pc_communality = sum_{k=1..6}(r_k^2)`
- `axis_purity = r_j^2 / six_pc_communality`; a zero denominator would be reported nonfinite and treated as failing selection.
- `target_is_largest_abs_loading` is true only when `|r_j| > max_{k != j}|r_k|`; an exact tie does not pass.
- Strength, purity, and dominance-gap ranks are descending within target PC, with trait name as deterministic tie-breaker.

The 240-row best-axis table selects the largest absolute saved correlation; exact ties are broken by lower PC number.

## Bootstrap

- Resamples: 2,000 role bootstrap samples, each of size 275 with replacement.
- Master seed: `20260920` using NumPy `default_rng`.
- The same sampled role indices are used for all 240 traits and all six PCs within a resample.
- Correlations are recomputed from saved role-level trait-affinity and PC-score observations.
- `P(target largest)` uses the same strict largest rule; exact ties do not count for any target.
- Percentile intervals use the empirical 2.5th and 97.5th percentiles.
- Existing sign-stability estimates are retained byte-for-byte from the saved association table; they are not rerun.

## Primary axis-specific marker rule

A trait-target row is a primary marker only if all four conditions hold:

1. it is in the original association family for that signed PC pole;
2. the target PC is its strict largest absolute PC1-PC6 association;
3. bootstrap `P(target largest) >= 0.95`;
4. observed `axis_purity >= 0.70`.

Sensitivity tables cross purity thresholds `0.60`, `0.70`, `0.80` with bootstrap-dominance thresholds `0.90`, `0.95`, `0.99`; all other conditions stay fixed. The primary cell is `0.70 x 0.95`.

## Classification of original association-family members

Classes are assigned in this order:

1. `AXIS_SPECIFIC_STRONG`: passes the full primary rule.
2. `NON_TARGET_DOMINANT`: observed target is not the strict largest absolute PC association.
3. `TARGET_DOMINANT_BUT_DIFFUSE`: observed target is largest, but observed axis purity is below 0.70.
4. `STRONG_CROSS_LOADING`: observed target is largest and purity is at least 0.70, but bootstrap target-dominance probability is below 0.95.

The reason field records each failed threshold. Cross-loading is descriptive, not a claim of psychological inferiority.

## Later-axis exploratory diagnostic

For each PC4-PC6 signed pole, separately list up to ten target-dominant traits ranked by descending purity, then descending target strength, requiring `|r_target| >= 0.30`. This list is exploratory and is never mixed with primary markers.

## Pareto frontier

Within each target PC, a trait is on the strength-purity Pareto frontier if no other trait has both at least as large `|r_target|` and at least as large axis purity, with one strictly larger. Exact duplicates are retained and ordered by trait name.

## Human-measurement mapping firewall

- The reviewer packet uses neutral family IDs and primary markers only.
- It exposes marker name, canonical definition, target correlation, axis purity, and dominance gap.
- It excludes PC number, role/persona evidence, prior PC interpretations, AA-2/AA-7 results, and previous human match labels.
- The candidate universe is the unchanged 126-construct `human_construct_library.csv`, plus item-only fallback when no scale adequately represents marker content.
- Match statuses remain: `STRONG_FAMILY_MATCH`, `PARTIAL_FAMILY_MATCH`, `FACET_OR_SUBCOMPONENT`, `ITEM_LEVEL_ONLY`, `POOR_MATCH`, and `NO_DEFENSIBLE_MATCH`.

## Evidentiary boundary

This analysis distinguishes strong association from axis specificity. It does not treat cross-loading as an error, equate a Qwen PC with a human construct, score or project a human respondent, use another model, test human/model correspondence, or choose a next experiment.
