# AA-12 Follow-up 4: preregistration for aggregate human-to-model profile correspondence

Status: frozen before any human/model similarity was calculated or viewed  
Date frozen: 2026-09-13  
Track: Track 1, independent profile-group correspondence  
Model used for analytical specification: GPT-5.5  

## Scope and evidentiary boundary

This study asks whether independently estimated aggregate SAPA latent-profile shapes resemble independently reconciled aggregate model persona-family shapes after both are expressed in the pre-existing coordinate-blind direct trait bridge. It does not score individuals into model space, compare prevalence, establish psychometric equivalence, establish natural personality types, or test a causal/shared latent mechanism.

The human classes, model clusters, consensus-family definitions, bridge decisions, item memberships, orientations, and eligibility decisions are immutable inputs. No model PCA coordinates, role neighborhoods, geometry-derived semantics, `ACCEPT_CLOSE` rows, new semantic mappings, new inference, or new activation extraction may enter this analysis.

## Frozen inputs

### Human profiles

- Numerical source: `research/outputs/cross_resolution_profile_banks/human/human_cross_resolution_profiles.csv`.
- Method source: the AA-12 six-category observed-cell product-multinomial mixture frozen at `6b2e460f19efca5d4dbb47487461790651d34208`; anonymous numerical profiles were frozen at `f0e55723eacc16730d4d9184bcb8bb9868458fb0`.
- Primary eligible K values: exactly `4, 5, 6, 7, 8, 10`.
- Human-stability sensitivity K values: exactly `4, 5, 6`.
- K=9 remains `DIAGNOSTIC / INELIGIBLE` and cannot enter any primary or sensitivity maximum, assignment, p-value, decision tier, or claim.
- Human profiles will not be refit, relabeled, merged, split, or prevalence-weighted.

### Model families

- Numerical source: `research/outputs/crossmodel_cluster_reconciliation/consensus_family_trait_profiles.csv` and its frozen source banks.
- Primary family set: exactly `MFamily_A`, `MFamily_B`, `MFamily_C`, `MFamily_D`.
- The primary three-model vectors are simple arithmetic means of the frozen Qwen, LLaMA, and Gemma within-model standardized family trait vectors at the reconciliation anchor Qwen K=6 / LLaMA K=9 / Gemma K=6. No human information enters those means.
- Secondary `MFamily_E` uses the already documented exact developmental recurrence `Q07_G`, `L09_I`, and `G06_A`. Its model-specific vectors are taken from the frozen K banks, and its secondary consensus vector is their simple arithmetic mean. E cannot enter the A-D global statistic or alter primary family definitions.
- The rejected creative/conceptual near-consensus region remains excluded. It will not be tested in this assignment because doing so is unnecessary for the preregistered questions and could invite post-result promotion.

### Frozen bridge and human measurement metadata

- Mapping source: `research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_trait_bridge_provisional_v1.csv`.
- Orientation and exact item membership source: `research/outputs/sapa_bridge_psychometric_audit/trait_proxy_item_scoring.csv`.
- Measurement-support source: `research/outputs/sapa_bridge_psychometric_audit/sapa_trait_bridge_psychometric_support_v1.csv`.
- Primary vocabulary: exactly the 45 `ACCEPT_DIRECT` traits, comprising 119 frozen trait-item rows and 96 unique SAPA items.
- Conservative vocabulary: exactly the 12 `ACCEPT_DIRECT` traits labeled `HIGH HUMAN-MEASUREMENT SUPPORT` (9) or `MODERATE SUPPORT` (3) in the frozen audit.
- The other direct traits remain in the primary 45: 30 `REDUNDANT / BROAD` and 3 `INSUFFICIENT` single-item mappings (`curious`, `dramatic`, `patient`). These limitations are metadata, not post-hoc exclusion rules.
- No `ACCEPT_CLOSE` row is allowed in either analysis.

## Common-space construction

### Human aggregate profiles

For each frozen human profile and each mapped SAPA item, the item expectation is

`E[item] = sum(c * P(response=c | profile))`, for categories c=1,...,6.

The raw SAPA V5 tab artifact must match SHA256 `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`. For every one of the 96 mapped items, its empirical mean, sample standard deviation (`ddof=1`), and observed count are computed from valid observed responses 1-6 only. Empty cells contribute nothing; there is no respondent-level imputation. Values outside 1-6 are an error.

The frozen orientation sign is applied as follows:

`z_oriented = orientation_sign * (profile_expected_raw - observed_item_mean_raw) / observed_item_sd_raw`.

This is algebraically identical to reverse-scoring both the profile expectation and population item mean as `7-x` when the sign is -1. Each human trait value is the unweighted arithmetic mean of its frozen oriented item z-scores. Reused SAPA items contribute once to each trait whose frozen proxy includes them; no reuse-derived or outcome-derived weight is applied. Only aggregate moments and aggregate latent-profile values may be saved.

### Model aggregate profiles

The frozen model trait values are already within-model standardized at the role level before family aggregation. For A-D, the Qwen/LLaMA/Gemma family-specific values are reused from the reconciliation output and their three-model arithmetic mean is the primary consensus vector. For E, the frozen Q07_G/L09_I/G06_A values are extracted from the K banks and averaged identically. The 45 direct trait rows and the frozen 12-row subset are selected by exact trait ID. Human measurements do not affect model normalization.

## Similarity and assignment

- Primary pairwise similarity: Pearson correlation across aligned trait dimensions.
- Secondary pairwise similarity: Spearman rank correlation across aligned dimensions.
- Centered cosine will not be separately interpreted because it is algebraically redundant with Pearson here.
- At each eligible human K, construct every human-profile by A-D correlation.
- Use an injective maximum-weight assignment: each of A-D is assigned to a distinct human profile, unmatched human profiles are allowed, and the total raw Pearson correlation is maximized with deterministic linear assignment. Ties are broken by lexicographically ordered family ID and then human profile ID through a fixed infinitesimal lexicographic penalty smaller than `1e-12`.
- Class proportions are never used as weights.
- The primary K statistic is the arithmetic mean of Fisher transforms `atanh(clip(r, -0.999999999999, 0.999999999999))` for the four assigned correlations. A back-transformed mean r is reported.
- The primary observed global statistic is the maximum mean Fisher-z over K=`4,5,6,7,8,10`. Maximizing K is a search result, not a true-K estimate.

## Search-adjusted bridge-permutation inference

### Primary 45-trait null

- Permutations: exactly 20,000.
- Seed: `2026091304`, NumPy `PCG64` through `numpy.random.default_rng`.
- In each draw, one random permutation of the 45 human trait columns is applied consistently to every human profile at every K. Model trait columns remain in canonical sorted-trait order. This preserves all human profile/cross-K structure and all model-family structure while destroying the human-to-model semantic alignment.
- For each draw, recompute all correlations, the optimal injective assignment at every eligible K, and retain the maximum mean Fisher-z across the six eligible K values.
- Empirical upper-tail p-value: `(1 + count(null_max >= observed_max)) / 20001`.
- The complete null maximum distribution is saved.

### Family-specific inference

For each A-D family, the observed statistic is its maximum positive-direction Pearson r over every human profile and every eligible K. Each permutation retains the same family-specific maximum over the identical search space. The same plus-one upper-tail p-value is used. The selected pair from the global injective assignment is also reported and is not substituted by the family-specific maximizer.

### Conservative 12-trait null

Repeat the complete global and family-specific pipeline over the frozen 12 dimensions with exactly 20,000 permutations and seed `2026091312`. This is a sensitivity analysis, not a replacement for the 45-trait primary analysis.

### Human-stability sensitivity null

Using the same 20,000 primary 45-trait permutations, recompute the global maximum while restricting K to `4,5,6`. This restriction is defined before outcomes and yields its own search-adjusted p-value.

## Frozen decision tiers

Family-specific positive evidence means observed family maximum r > 0 and search-adjusted p <= .05.

`STRONG AGGREGATE CORRESPONDENCE` requires all of:

1. primary 45-trait global p <= .05;
2. at least three of four A-D families meet the family-specific positive-evidence rule;
3. the 12-trait best back-transformed mean r is positive and at least three of the four primary 45-trait selected pairs have positive 12-trait correlations when evaluated at those same pair identities; and
4. the K=4-6 sensitivity has p <= .05 and a back-transformed mean r at least 80% of the primary back-transformed mean r.

`MODERATE / PARTIAL AGGREGATE CORRESPONDENCE` requires the primary global p <= .05 but at least one other strong-tier condition fails.

`WEAK / ABSENT AGGREGATE CORRESPONDENCE` applies when the primary global p > .05. No robustness result can promote a failed primary global test.

For MFamily_E only, p <= .05 with positive r is described as adjusted evidence, `.05 < p <= .10` as suggestive, and p > .10 as no detectable adjusted counterpart. E never changes the primary tier.

## Predeclared robustness and descriptive analyses

### K=9 diagnostic

After the primary numerical freeze, compute its A-D similarity matrix and injective score. Mark every row `DIAGNOSTIC / INELIGIBLE`. It has no inferential or selection role.

### Model-specific replication

For each of the four pairs selected at the primary maximizing K, hold the human counterpart fixed and report Pearson/Spearman correlations against the frozen consensus, Qwen, LLaMA, and Gemma family vectors. Report range and sign agreement. No model-specific reassignment is allowed. Also report fixed-pair leave-one-model-out consensus correlations for Qwen+LLaMA, Qwen+Gemma, and LLaMA+Gemma as descriptive sensitivity.

### Human cross-resolution persistence

Use only `human_adjacent_k_continuity.csv`. A lineage edge is recognized when `mutual_nearest=True`. For every primary selected human profile, trace connected mutual-nearest parents/descendants across available adjacent K values. At each lineage node, record its closest A-D family, correlation, whether that family matches the starting selected family, assignment status, eligibility, and frozen human stability metadata. No new human taxonomy is inferred.

### Relaxed split/merge browsing

For all eligible human profiles, report the best and second-best A-D family by Pearson r, their margin, and whether the best family matches a mutual-nearest lineage's family. This many-to-one view is descriptive only and cannot replace the injective test.

### Response style

The frozen human analysis found a material response-style warning at every K while retaining 96.5%-99.0% of between-profile item-pattern variance after generic response-level removal. No independently frozen response-style correction in the exact 45-trait proxy space exists. A new correction would introduce discretionary post-hoc modeling, so no separate corrected correspondence statistic will be created. The observed-item marginal z transformation and Pearson profile-shape correlation already remove item baselines and profile-wide additive elevation, respectively, but do not eliminate all response-style structure. A machine-readable `NOT_RUN_NO_FROZEN_TRANSFORM` record and the caveat will be retained.

## Split/merge and persistence interpretation rules

- A candidate subdivision is described only when two or more human profiles at the same K share the same best A-D family and each has positive r; inferential language uses only that family's max-search adjusted p-value.
- A between-family/ambiguous profile is one whose top-two correlation margin is <= 0.10; this threshold is descriptive and carries no p-value.
- A profile is descriptively unmatched when its best r <= 0 or the associated family-specific adjusted p > .05.
- Persistent correspondence requires the same best family at two or more profiles connected by mutual-nearest adjacent-K edges. An isolated match may still be reported but not called persistent.

## Visualization freeze

Figures will use deterministic ordering and cannot affect inference:

1. SAPA item heatmaps/ridges for K=4, maximizing eligible K, K=10, plus K=6 if needed to ensure an intermediate view. The 96 unique items are ordered by lexicographically first frozen trait owner and numeric item ID; all trait reuse and exact wording remain in a searchable table.
2. Human 45-trait profile ridges using alphabetical trait order.
3. Model A-D and separate E 45-trait ridges using the same alphabetical order.
4. Human-by-model similarity heatmaps for every eligible K.
5. K-level Fisher-z and back-transformed score plot with frozen stability metadata and K=4/K=10 anchors.
6. Observed primary maximum against the permutation-max null.
7. Primary injective assignment diagram.
8. Mutual-nearest cross-resolution persistence view.
9. Side-by-side 45- versus 12-trait sensitivity summary.
10. Consensus/Qwen/LLaMA/Gemma fixed-pair replication plot.

Color scales are fixed symmetrically where values have a meaningful zero. Profile and family labels remain anonymous IDs during numerical work. Exact SAPA wording and post-freeze family descriptions may be viewed only after primary and robustness numerical freezes are committed.

## Stopping and reproducibility rules

- Missing required input rows, duplicate trait/profile/item keys, nonfinite values, response values outside 1-6, source-hash mismatch, noninjective assignments, or inconsistent K/family sets stop the run.
- Floating-point ties follow the deterministic rule above; file rows are sorted by explicit key before writing.
- All numeric outputs retain at least 12 significant digits where practical.
- A full deterministic rerun must reproduce all core CSV/JSON outputs byte-for-byte or the discrepancy must be reported.
- Respondent IDs, rows, masks, posteriors, and individual scores are prohibited outputs.
- Semantic interpretation cannot change mappings, profiles, assignments, K values, family definitions, or the decision tier.
