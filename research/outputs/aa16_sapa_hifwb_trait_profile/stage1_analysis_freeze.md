# AA-16 Stage 1 analysis freeze · 2026-09-17

Status: frozen before calculating any human trait–HiFWB association. This
stage constructs a measured-or-unavailable profile over the 240 shared model
trait labels. It does **not** inspect or use model PC coordinates, fit a model
wellbeing direction, score personas, build a viewer, run a model, or incur GPU
cost.

## Sources and joins

- The 240 trait labels are read from the Qwen records of AA-14's
  `trait_pc_scores_all.csv` only to establish the shared vocabulary. The
  candidate crosswalk supplies the frozen label-to-description text. No PC
  coordinate is loaded into the association calculation.
- Semantic mapping is the unchanged 74-row provisional bridge:
  45 `primary_direct`, 29 `secondary_close`. Its preceding 240-row candidate
  crosswalk and the 74-row psychometric audit supply provenance and
  human-measurement support flags. All other labels remain absent; a rejected
  candidate is not promoted to close or ambiguous to enlarge coverage.
- The 13 DIRECT HiFWB items and their signs come from the byte-frozen
  `wellbeing_item_freeze.csv` (SHA256
  `dcac8f8d2e82c6fa337a8c34472b8b1901d7c709823618dd4bf614ed885a46e0`).
  The four CLOSE auxiliary rows are excluded. The composite is the AA-10/AA-13
  historical mean of available positively oriented, full-cohort standardized
  DIRECT items, requiring at least two observed items.
- External SAPA V5, DOI `10.7910/DVN/SD7SVE`, file
  `sapaTempData696items08dec2013thru26jul2014.tab`, must match SHA256
  `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`
  and 23,679×719 dimensions. The previously published/user-provided schema
  fingerprint `787f539747deee8da85bc64da9c3407eaf741f6da927dcbec7ec79b2a40260c`
  contains only 63 hex characters. Before outcome analysis, the 719-column
  header independently yielded the 64-character SHA256
  `787f539747deee8da85bc64da9c3407eaf741f6da9277dcbec7ec79b2a40260c`
  using `SHA256("\\x1f".join(header_names))`. This correction changes no data.

## Predictor and outcome scores

- The prior psychometric audit's trait-specific `REVERSE_BY_TRAIT` item signs
  are reused exactly, extracted from its source script without importing or
  changing its analysis. Each reversed 1–6 response becomes `7−x`, then each
  item is standardized using its oriented full-cohort observed mean and
  sample SD (`ddof=1`). The respondent trait proxy is the unit-weight mean of
  available standardized items. Because the preceding audit estimated proxy
  covariance from pairwise-complete item correlations rather than freezing a
  respondent-level proxy score, this Stage 1 respondent scoring rule is a
  prospective bridge extension, not an alleged reproduction of a prior
  respondent-level trait score.
- Require at least two observed predictor items for a 2+ item proxy and one
  for a genuinely single-item proxy. This matches AA-13's multi-item
  scale-eligibility principle and prevents a multi-item proxy from silently
  becoming a one-item measure. The resulting N is expected to be limited by
  SAPA planned missingness. No missing response is imputed.
- Every HiFWB indicator is oriented so higher means more wellbeing, then
  full-cohort standardized with sample SD. The composite uses the frozen
  AA-10/AA-13 two-observed-item rule. The 13 individual outcomes require the
  corresponding item to be observed.
- Exclude a predictor from an outcome whenever their item sets overlap. For
  the composite, **any** overlap with the 13 DIRECT items excludes the
  predictor. No item is dropped post hoc from a predictor to rescue a match.

## Association and reporting rules

- Primary: Pearson correlation on respondent pairs satisfying both scores.
  Sensitivity: Spearman correlation on the same eligible pairs, using average
  ranks for ties. Positive signs always mean a stronger proxy associates with
  higher wellbeing.
- An eligible pair count below 30, a constant score, an absent mapping, or an
  outcome-item overlap produces an explicit unavailable association, never a
  zero or imputed value. Record actual eligible N even for low-N cases.
- Confidence intervals are descriptive two-sided 95% Fisher-z intervals
  (`atanh(r) ± 1.959964/√(N−3)`, transformed back by `tanh`); Spearman uses
  the same large-sample approximation and is labeled approximate. No
  significance threshold is used to turn a mapping on or off.
- Preserve all 240 labels for each of 14 outcomes in the long profile, with
  blank numeric fields and a status/reason for unavailable cells. The
  composite profile has exactly 240 rows. Direct mapping is the primary tier;
  close mappings are clearly labeled sensitivity. Ambiguous mappings never
  enter observed results.
- Exact duplicate groups are defined before outcome calculation by identical
  sorted SAPA item-ID sets, including inverse-keyed aliases. The 240-row
  descriptive profile retains each model label but tags shared human sources.
  Summary counts distinguish model labels from unique item-set constructs.
  Shared scale or partial item reuse is additionally flagged, not falsely
  treated as an exact duplicate.
- Indicator-profile comparisons use only shared observed direct constructs,
  collapse exact duplicate item-set groups, and are descriptive. No
  trait-PC, viewer, persona, or model-representation inference follows from
  Stage 1.

## Privacy, determinism, and status

The script reads external respondent rows only in memory and exports aggregate
correlations, Ns, mapping metadata, and audits. It never writes respondent
identifiers, respondent scores, source rows, or raw model tensors. No random
resampling or stochastic model fit is required in Stage 1.

AA-15's provenance repair remains valid. Its prospective direct-model HiFWB
extraction was **not run**, incurred **no cost**, and is **deferred** because it
is unnecessary for this SAPA-mediated Stage 1 question. Its scripts and
freezes remain in the AA-15 history for a different, later question.
