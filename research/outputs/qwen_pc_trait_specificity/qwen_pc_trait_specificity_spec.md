# Qwen PC Trait Specificity: Frozen Analysis Specification

Status: frozen before computing or inspecting trait-level specificity results.

Freeze basis: validated AA-1 commit `667acdd634bfb8c39d40432fe60f0c5ef3bbbeeb`.

## Scope and terminology

A **PC-associated trait** is an unchanged member of the AA-1 inventory: target
`|Pearson r| >= 0.50`, within-PC BH-FDR `q < 0.01`, and target-sign stability
`>= 0.95` over the existing 2,000 role bootstraps.

A **PC-defining trait** is PC-associated and its target PC has the largest
absolute correlation among PC1-PC6 in at least 95% of the new joint role
bootstrap resamples. Strength and specificity remain separate quantities.

The analysis uses only the saved 275 Qwen roles, their 240 saved activation-
cosine trait profiles, and saved Qwen PC1-PC6 coordinates. No human respondent
records, other model values, AA-7 results, inference, or activation extraction
are inputs.

## Cross-PC metrics

For every one of the 240 traits and each target in PC1-PC6, retain all six
signed Pearson correlations and compute:

- `target_pearson_r`, `target_abs_r`, and `target_r_squared`;
- the largest absolute off-target correlation, its PC, and its signed value;
- `specificity_margin = target_abs_r - largest_offtarget_abs_r`;
- `specificity_ratio = target_abs_r / (largest_offtarget_abs_r + 1e-12)`;
- `pc1_6_concentration_fraction = target_r_squared / sum(r_PC1^2 ... r_PC6^2)`.

The concentration fraction is concentration within the first six Qwen PCs
only. It is not the share of total trait activation-space variance uniquely
explained by the target PC. Exact ties for the largest off-target are broken by
the lower PC number for the reported label. Exact target/off-target ties count
as target-largest in the bootstrap probability; such ties are separately
counted for audit.

## Joint specificity bootstrap

Use 2,000 bootstrap resamples of the 275 roles with NumPy PCG64 seed
`20260912`. A single role-index resample is shared across all 240 traits and all
six PCs so cross-PC comparisons are paired. Pearson correlations are recomputed
within each resample. Report the target-largest probability and the median,
2.5th percentile, and 97.5th percentile of target absolute correlation, largest
off-target absolute correlation, specificity margin, specificity ratio, and
PC1-PC6 concentration fraction. Quantiles use NumPy's default linear method.

The existing AA-1 sign-stability estimates, q-values, and membership decisions
are imported unchanged rather than silently replaced by the joint bootstrap.

## Frozen primary rule and descriptive tiers

The primary PC-defining rule is:

1. unchanged AA-1 PC-associated membership; and
2. bootstrap target-is-largest probability `>= 0.95`.

No fixed off-target cutoff is used.

Passing traits receive mutually exclusive display tiers:

- `HIGHLY CONCENTRATED`: primary PC-defining and observed concentration `>= 0.75`;
- `MODERATELY CONCENTRATED`: primary PC-defining and observed concentration
  `>= 0.50` and `< 0.75`;
- `TARGET-DOMINANT`: primary PC-defining and observed concentration `< 0.50`;
- `BROAD / CROSS-PC`: PC-associated but not primary PC-defining;
- `NOT PC-ASSOCIATED`: does not meet the unchanged AA-1 rule for that target.

The 0.50 and 0.75 concentration cutoffs are descriptive, not hypothesis tests.
Sensitivity counts additionally use concentration cutoffs 0.60, 0.70, and
0.80.

## Pareto view

Within each PC and observed target-correlation pole, identify the Pareto
frontier across all 240 traits for higher target absolute correlation, higher
specificity margin, and higher observed concentration fraction. Trait A
dominates trait B if A is at least as large on all three metrics (tolerance
`1e-12`) and strictly larger on at least one. This all-trait universe makes the
view threshold-light; membership in the original AA-1 associated family is
retained as a separate flag.

Scope clarification recorded after the first mechanical run but before final
reporting: the initial text limited the frontier to associated traits. The
all-trait universe above follows the request's threshold-light purpose more
literally. This clarification does not alter the frozen primary PC-defining
rule, its bootstrap probability, any single-trait metric, or any PC-defining
membership.

## Sensitivity grid

Without selecting a preferred result after inspection, report all nine
combinations of target `|r|` thresholds 0.40, 0.50, and 0.60 and bootstrap
target-largest thresholds 0.90, 0.95, and 0.99. BH-FDR `< 0.01` and existing
sign stability `>= 0.95` remain fixed. For every PC/pole/grid cell report the
associated count, target-dominant count, and counts additionally reaching
observed concentration 0.60, 0.70, and 0.80.

## Secondary descriptive composites

Composites cannot change single-trait selection.

- Canonical reference: if provenance is exact, use the saved Qwen Affiliation
  visualization formula—an equal-weight mean of the within-Qwen midrank
  percentiles of `empathetic`, `agreeable`, and `altruistic`—without alteration.
- Per PC/pole: average the raw saved activation-cosine profiles of the top three
  primary target-dominant traits ranked by observed concentration fraction,
  with target absolute correlation then trait name as deterministic tie-breaks.
- Per PC/pole: separately average the top three Pareto-frontier traits under the
  same ranking if the member set differs.

Each available composite is correlated with PC1-PC6 and receives the same
observed strength, off-target, margin, ratio, and concentration metrics. These
are labeled `SECONDARY / DESCRIPTIVE COMPOSITES`.

## Human-mapping refinement

The frozen AA-1 family-to-SAPA judgments and their semantic statuses remain
unchanged. For every prior mapping row, intersect its explicitly covered Qwen
traits with the PC-defining, highly concentrated, and Pareto sets for the same
PC/pole. Family-level proposals that do not enumerate a narrower covered subset
are treated as covering the associated traits listed by the frozen judgment,
not as new semantic judgments. Report covered and unmatched diagnostic traits;
do not score respondents or interpret coverage as human/model correspondence.
