# AA-5 frozen analysis specification

Status: frozen before occupational trait means, uncertainty estimates, stability statistics, variance decompositions, discrimination results, or feasibility labels were computed.

Freeze date: 2026-09-11

Starting commit: `7914d01f7d9c23060fe199815a90e547241d9682`

Branch: `codex/aa5-nlsy97-occupation-stability`

## Scientific scope

This is a human-only feasibility analysis. It asks whether public-use NLSY97 occupational groups support reproducible five-domain personality centroids for a possible later study. It does not test human/model correspondence. Model activations, model personality scores, model principal-component coordinates, and model geometry are prohibited inputs. The pre-existing persona-to-occupation crosswalk may be joined only after human stability tiers are assigned, to list possible future comparison groups.

## Source data and analytic cohorts

The respondent-level source is the official NLS Investigator public-use extract `human_trait_dataset_feasibility_final.csv` documented by the canonical AA-1 NLSY97 source manifest. Respondent rows and IDs remain gitignored and are never written to an output artifact.

The primary analytic cohort requires all of the following:

1. all ten Round-12 TIPI items are in `1..7`;
2. `CV_MAINJOB_FLG` selects a roster position with an official 2002 Census occupation code;
3. the code is not `9920`, because that code denotes no recent occupation rather than an occupation;
4. the Round-12 cumulative-cases sampling weight `T2022500 / 100` is positive; and
5. `VSTRAT` and `VPSU` are valid.

Code `9830` (military, rank not specified) may be reported as a narrow Census cell and assigned to SOC major group `55-0000`, but it has no official SOC minor-group code and is omitted at the intermediate level.

Cell-specific public outputs require unweighted analytic `N >= 10`. Counts of omitted cells and respondents are reported only in aggregate. No respondent identifiers are retained. This conservative suppression rule is stricter than needed to reproduce the already-public AA-1 aggregate counts and is not evidence that the public-use source imposes a particular universal threshold.

## Personality scoring

TIPI scoring follows the instrument developer's key. Reverse-scored items are transformed as `8 - item`; each domain is the arithmetic mean of its two keyed items:

- Extraversion: items 1 and 6R.
- Agreeableness: items 2R and 7.
- Conscientiousness: items 3 and 8R.
- Emotional Stability: items 4R and 9.
- Openness to Experience: items 5 and 10R.

No item imputation is performed. Emotional Stability remains positively oriented; an optional Neuroticism interpretation would reverse its sign and is not used in the centroid.

For Round 6, the official extract codebook wording overrides inconsistent direction labels in the canonical AA-1 convenience manifest. All four-item scales are oriented toward more Agreeableness or Conscientiousness before averaging:

- Conscientiousness: `6-S0920000`, `S0920100`, `6-S0920200`, `S0920300`.
- Agreeableness: `S0920400`, `6-S0920500`, `6-S0920600`, `S0920700`.

The correction is auditable against the official codebook included with the extract. Round-6 Goldberg respondents were limited by design to respondents age 14 or younger at the end of 1996, so recurrence estimates do not represent the full original cohort.

Round-12 industriousness, Round-12 traditionalism, and Round-16/17 grit are inventoried in the source manifest but are not combined with TIPI and are not used to construct an omnibus score.

TIPI reliability is described using the globally weighted inter-item correlation and Spearman-Brown two-item coefficient for each domain. These coefficients are limitations, not inclusion criteria. TIPI is treated as a very brief, low-resolution measure.

## Occupational levels fixed without trait outcomes

The official 2002 Census-to-2000-SOC code field defines every aggregation. No psychological regrouping or trait-dependent regrouping is allowed.

- `narrow`: four-digit 2002 Census occupation code and official Census title.
- `intermediate`: 2000 SOC minor group. For a valid SOC string `MM-Xabc`, the group is `MM-X000`. Each Census code maps only when all listed SOC components imply one minor group.
- `broad`: 2000 SOC major group `MM-0000`, with official major-group title. Code `9830` is assigned to `55-0000`; code `9920` is excluded.

The generated aggregation crosswalk is saved before analysis results and includes the source SOC string and any nonstandard treatment. Semantic-cost discussion uses only official titles and the number of distinct narrow occupations inside a parent group; trait means cannot change mappings.

## Centroid and descriptive estimands

Each TIPI domain is standardized across the full primary analytic cohort using its survey-weighted global mean and survey-weighted population standard deviation. All weighted and unweighted occupational centroids use these same five global transformations.

The primary centroid is the vector of five Round-12 cumulative-case-weighted standardized domain means. Unweighted means are sensitivity estimates. Raw-scale weighted means and standard deviations are also retained.

For every nonsuppressed cell, the descriptive table reports analytic N, all valid-occupation N, TIPI-complete N and rate, sum of Round-12 weights, approximate mean age (`2008 - birth year`), female share, education categories based on the nearest available Round-13 highest-grade-completed measure, class-of-worker shares, freelance/contractor share when observed, domain means and standard deviations, and design-based standard errors and intervals. Education is explicitly labeled as a 2009 follow-up measure, not same-wave attainment.

Within-cell heterogeneity is the square root of the survey-weighted mean squared Euclidean distance between respondent five-domain standardized profiles and the weighted cell centroid.

## Survey variance and confidence intervals

Round-12 weights use the documented two implied decimal places. VSTRAT and VPSU define strata and primary sampling units. Occupational cells are treated as survey domains, not as separately sampled surveys.

For a weighted domain mean, the Taylor-linearized respondent contribution is

`z_i = w_i d_i (y_i - mean) / sum(w_i d_i)`.

Contributions are summed within PSU. Within each stratum with `m_h` PSUs, variance is

`m_h/(m_h-1) * sum_j (z_hj - mean_h(z_hj))^2`,

then summed across strata. Intervals use a t critical value with design degrees of freedom equal to the number of PSUs minus the number of strata represented in the full primary analytic cohort. Standard errors are not simple-random-sample standard errors.

## Design-respecting bootstrap

Random seed: `20260911`.

Replicates: 500.

Within every VSTRAT, the observed number of PSUs is sampled with replacement from that stratum's PSUs. Respondent weights are multiplied by their PSU selection counts. Because the released design has two VPSUs per VSTRAT, replicate deviations from the full estimate are rescaled by `sqrt(2)` before intervals, covariance, and displacement summaries are computed. If the design audit does not confirm two PSUs in every represented stratum, analysis must stop rather than silently use this rescaling.

For every nonsuppressed cell the output contains per-domain 2.5% and 97.5% intervals, the 5-by-5 centroid covariance (stored as its 15 unique elements), mean/median/95th-percentile Euclidean displacement from the full centroid, root trace covariance, and valid-replicate count.

## Split-half stability

Random seed sequence: `20260911 + split_index`, for 500 deterministic splits.

Respondents are randomly partitioned within each occupational cell into two subsets differing in size by at most one. Survey weights remain attached to respondents. For each split, the two weighted five-domain centroids are compared with:

- Euclidean distance;
- uncentered cosine similarity;
- profile-mean-centered cosine similarity;
- Pearson correlation across the five dimensions; and
- Kendall rank correlation across the five dimensions.

Centered cosine and Pearson correlation are mathematically redundant when both are defined; both are saved because they were requested, and neither alone determines feasibility. Median, 5th percentile, and 95th percentile are reported for every metric. Cells with fewer than ten respondents are suppressed.

## Sample-size stability curve

Subsample sizes: `10, 20, 30, 40, 50, 75, 100, 150, 200, 300, 500` where supported.

Random seed sequence: `20260911 + 100000 * level_index + 1000 * size + repeat`.

For each level, only cells with at least `max(2*n, n+20)` respondents contribute at a requested subsample size. Three hundred without-replacement subsamples are drawn per eligible cell. Their survey-weighted centroids are compared with the full-cell centroid using Euclidean distance. Cell-level mean, median, 5th, and 95th percentiles are saved, followed by level-level summaries that give every eligible occupation equal weight. The full-cell centroid is a finite-sample reference, not a known population truth.

## Granularity tradeoff

Every nonsuppressed narrow cell is linked to its frozen intermediate and broad parents. The tradeoff table reports parent N gain and number of distinct child codes, within-cell heterogeneity, bootstrap displacement, split-half distance, and assigned feasibility tier at all available levels. Broadening is described as a reliability/specificity tradeoff, not assumed to preserve the narrow occupation's meaning.

## Shrinkage sensitivity

For each level and domain, an empirical-Bayes normal-normal model uses the design-weighted raw cell mean and its Taylor-linearized sampling variance. The prior mean is the global weighted mean (zero on the standardized scale). Between-cell variance is estimated by the nonnegative method-of-moments difference between the weighted variance of cell means and their average sampling variance. Posterior means, posterior standard errors, shrinkage weights, and absolute shrinkage are reported for cells with `N >= 10`.

This is a sensitivity analysis. Shrunken estimates do not change observed N, stability metrics, or feasibility tiers.

## Round-6/Round-12 recurrence

Round-6 Goldberg A/C scores are standardized globally in the Round-6 complete-plus-occupation cohort. Round-12 TIPI A/C scores use the primary standardization.

Population-level occupational recurrence includes frozen occupation cells with at least 20 complete observations in each round. Because a Round-6 survey-year weight was not included in the canonical extract, this comparison is unweighted at both rounds. It reports paired cell means and across-cell Pearson and Spearman correlations.

Stable-occupation analyses require the same respondent to remain in the identical narrow, intermediate, or broad group at rounds 6 and 12 and require at least 20 stable respondents per reported cell. Both unweighted and Round-12-weighted paired cell means are saved. Cross-wave differences are not interpreted solely as personality change.

## Variance decomposition

For each domain at narrow and broad levels, weighted total variance is decomposed exactly into:

- between-occupation variance: weighted variance of cell centroids, weighted by cell population weight;
- within-occupation variance: weighted mean squared deviation from the appropriate cell centroid; and
- descriptive ICC: between / (between + within).

All eligible primary-cohort respondents contribute internally, including members of cells below the public reporting threshold; only aggregate decomposition results are emitted. Bootstrap 95% intervals use the frozen design-respecting replicates. An unweighted sensitivity decomposition is also reported.

## Descriptive occupation discriminability

For each level, eligible classes have `N >= 50`; the analysis runs only if at least five classes qualify. A fixed multinomial logistic regression (`C=1`, L2 penalty, no hyperparameter search) uses the five standardized TIPI domains. Ten repeats of stratified five-fold cross-validation use seeds `20260911..20260920`. Class balancing is applied only in model fitting. Held-out balanced accuracy is compared with the `1/K` uniform multiclass baseline. This is a descriptive control, not an optimized prediction competition and not evidence of causal occupational effects.

## Frozen feasibility tiers

Feasibility uses observed N and empirical vector stability. Correlation metrics do not gate tiers because a five-element, near-zero profile makes them unstable even when absolute centroid error is small.

`STRONG CENTROID` requires all of:

- `N >= 100`;
- at least 475 valid bootstrap replicates;
- bootstrap mean displacement `<= 0.25`;
- bootstrap 95th-percentile displacement `<= 0.40`;
- split-half median Euclidean distance `<= 0.45`;
- split-half 95th-percentile distance `<= 0.80`; and
- bootstrap 95th-percentile displacement / within-cell heterogeneity `<= 0.20`.

`MODERATE / EXPLORATORY` requires all of:

- `N >= 50`;
- at least 450 valid bootstrap replicates;
- bootstrap mean displacement `<= 0.40`;
- bootstrap 95th-percentile displacement `<= 0.60`;
- split-half median Euclidean distance `<= 0.70`;
- split-half 95th-percentile distance `<= 1.20`; and
- bootstrap 95th-percentile displacement / within-cell heterogeneity `<= 0.30`.

A narrow or intermediate cell that fails the moderate criteria is `BROAD-FAMILY ONLY` when its broad parent is strong or moderate. All other cells are `UNSTABLE / TOO SPARSE`. Broad-level cells cannot receive `BROAD-FAMILY ONLY`.

The thresholds reflect five-dimensional standardized error: independent-domain sampling alone implies a rough centroid standard error proportional to `sqrt(5/N)`. They are fixed before empirical trait results. The earlier N>=20/50/100 cutoffs are evaluated against the empirical stability curve and these joint rules; they are not treated as conclusions.

## Future-role candidate join

Only after tiers are assigned, nonsuppressed occupation codes are joined to the pre-existing conservative AA-1 persona-to-occupation crosswalk. Output wording remains “respondents in occupation X.” The join retains model-role names and existing translation quality only. It never loads model data and never relabels human respondents as personas.

## Reproducibility and boundaries

All stochastic outputs use the seeds above. CSV columns are ordered deterministically; rows are sorted by fixed keys; JSON uses sorted keys and a fixed generated timestamp supplied by the runner. Verification reruns the analysis into a temporary directory and compares deterministic artifact hashes.

No GPU, RunPod, model inference, activation extraction, or external model API is permitted. No model geometry may be imported. No respondent-level output, respondent ID, human-to-model projection, persona assignment, crime/persona mapping, or optimization against model results is permitted.
