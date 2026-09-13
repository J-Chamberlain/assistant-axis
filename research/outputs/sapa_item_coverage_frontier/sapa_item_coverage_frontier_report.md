# SAPA item-coverage frontier for Track 1

## Scope and result

This descriptive AA-12 analysis measures raw response availability in the SAPA V5 behavioral-item matrix before any respondent filter, item panel, common feature space, clustering, imputation, construct scoring, or human/model match is chosen. The primary result is a **greedy nested coverage frontier**, not a mathematically proven global Pareto frontier. Threshold selection is deferred to the user.

The release contains 23,679 respondent rows and all 696 canonical behavioral items. Every respondent ID is unique (0 duplicates), so no rows were deduplicated. The most-observed item is `q_1867` with 6,096 responses (25.744%); the least-observed is `q_1825` with 2,304 (9.730%). Consequently, 0 items reach 50% marginal coverage. This low marginal coverage is expected under SAPA's random-subset administration and is not ordinary item nonresponse.

## Data-integrity audit

- Source: Harvard Dataverse SAPA V5, *Selected personality data from the SAPA-Project: 08Dec2013 to 26Jul2014*, DOI `10.7910/DVN/SD7SVE`, CC0 1.0.
- Respondent matrix: `sapaTempData696items08dec2013thru26jul2014.tab`; SHA256 is recorded in `source_manifest.json`. Raw respondent data remain gitignored and are not copied into this output.
- Canonical dictionary: `research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv`, cross-checked against raw `ItemInfo696.csv`.
- Dimensions: 23,679 rows × 719 columns: 696 canonical `q_*` behavioral items and 23 excluded respondent-ID/demographic/derived fields.
- Response coding: the only nonmissing behavioral-item values are integers 1–6 (`1=Very Inaccurate`, `6=Very Accurate`).
- Missing coding: in the raw behavioral-item cells, missing values are empty tab fields. No literal `NA` occurs in the 696-item matrix. Empty fields alone count as missing; all 1–6 answers count as recorded.
- Duplicate handling: RID was loaded only for a uniqueness count, then discarded. There are 0 duplicate RIDs, so no rows were removed or combined.
- Structural availability: SAPA used planned random-subset item administration. The release provides no cell-level planned-versus-unplanned flag, so those mechanisms cannot be separated. All 696 item columns exist, but individual respondents see only subsets.
- Waves/forms: this is one dated V5 extract and has no wave or form indicator. No wave/form split or adjustment was applied.
- Demographics excluded: `RID, gender, relstatus, age, marstatus, height, BMI, weight, exer, smoke, country, state, ethnic, education, jobstatus, occPrestige, occIncomeEst, p1edu, p1occPrestige, p1occIncomeEst, p2edu, p2occPrestige, p2occIncomeEst` were excluded from item eligibility and coverage calculations.

## 1. Marginal item coverage

Marginal coverage counts each item separately. It does **not** establish that the same respondents answered other items at the same marginal threshold. In particular, an item with 90% coverage would not imply that 90% of respondents share complete profiles across all such items.

| Marginal threshold | Items meeting threshold | Share of 696 items |
|---:|---:|---:|
| 100% | 0 | 0.000% |
| 99% | 0 | 0.000% |
| 95% | 0 | 0.000% |
| 90% | 0 | 0.000% |
| 80% | 0 | 0.000% |
| 70% | 0 | 0.000% |
| 60% | 0 | 0.000% |
| 50% | 0 | 0.000% |
| 25% | 14 | 2.011% |
| 20% | 16 | 2.299% |
| 15% | 122 | 17.529% |
| 10% | 687 | 98.707% |


Full item-level counts and percentages are in `sapa_item_response_rates.csv`; the threshold summary is in `sapa_marginal_coverage_thresholds.csv`.

## 2. Joint / nested profile coverage

The sequence starts with the item having the largest marginal response count. At each step it adds the remaining item that maximizes the number of respondents answering **every** item in the expanded panel. Exact ties are resolved by (1) higher marginal response count and (2) earlier position in the canonical 696-item dictionary. Item wording, scale membership, construct names, and psychological content never enter selection.

The relaxed ≥95%, ≥90%, and ≥80% curves are evaluated on the **same nested item order**. For panel size `k`, the required number answered is `ceil(level × k)`. These are descriptive recovery curves only; respondents below 100% are not treated as complete and no value is imputed.

The strict curve has a visually clear, very steep early bend: 6,096 respondents remain at one item, 1,455 at two, 358 at three, 103 at four, and 41 at five. This describes the coverage geometry; it does not nominate any one of those panel sizes. Once the greedy strict cohort becomes tiny, the algorithm can preserve an idiosyncratic respondent for a long tail (one strict-complete respondent from panel sizes 137 through 294). That tail is algorithmically valid but is not evidence of a broadly usable cohort. Relaxed counts can rise at occasional steps because `ceil(level × k)` does not increase at every step while a newly added answered item can move respondents across the fixed integer requirement.

| Items in nested panel | Complete respondents | Complete % | ≥95% answered | ≥90% answered | ≥80% answered |
|---:|---:|---:|---:|---:|---:|
| 1 | 6,096 | 25.744% | 6,096 | 6,096 | 6,096 |
| 2 | 1,455 | 6.145% | 1,455 | 1,455 | 1,455 |
| 3 | 358 | 1.512% | 358 | 358 | 358 |
| 4 | 103 | 0.435% | 103 | 103 | 103 |
| 5 | 41 | 0.173% | 41 | 41 | 276 |
| 6 | 26 | 0.110% | 26 | 26 | 115 |
| 7 | 19 | 0.080% | 19 | 19 | 71 |
| 8 | 15 | 0.063% | 15 | 15 | 43 |
| 9 | 13 | 0.055% | 13 | 13 | 26 |
| 10 | 11 | 0.046% | 11 | 20 | 62 |
| 11 | 9 | 0.038% | 9 | 16 | 31 |
| 12 | 8 | 0.034% | 8 | 11 | 22 |
| 15 | 7 | 0.030% | 7 | 9 | 20 |
| 18 | 6 | 0.025% | 6 | 7 | 9 |
| 22 | 5 | 0.021% | 6 | 6 | 6 |
| 23 | 4 | 0.017% | 5 | 6 | 6 |
| 39 | 3 | 0.013% | 4 | 4 | 4 |
| 64 | 2 | 0.008% | 3 | 3 | 3 |
| 137 | 1 | 0.004% | 2 | 2 | 2 |
| 294 | 1 | 0.004% | 1 | 1 | 1 |
| 295 | 0 | 0.000% | 1 | 1 | 1 |
| 309 | 0 | 0.000% | 1 | 1 | 1 |
| 310 | 0 | 0.000% | 0 | 1 | 1 |
| 326 | 0 | 0.000% | 0 | 1 | 1 |
| 327 | 0 | 0.000% | 0 | 0 | 1 |
| 367 | 0 | 0.000% | 0 | 0 | 1 |
| 368 | 0 | 0.000% | 0 | 0 | 0 |
| 696 | 0 | 0.000% | 0 | 0 | 0 |

The strict frontier first reaches one or fewer complete respondents at panel size 137 and zero at panel size 295. The full 696-step sequence is preserved in `sapa_nested_coverage_frontier.csv`, with the exact availability-only item order in `sapa_nested_item_order.csv`.

## Visual interpretation

`sapa_coverage_frontier.png` shows the full sequence and an early-panel symlog detail. Sharp changes in slope are descriptive coverage tradeoffs, not psychological findings and not a threshold recommendation. Any visually apparent bend should be treated as a region for later scientific consideration; AA-12 deliberately does not select an elbow, panel size, respondent cohort, complete-case rule, or partial-profile method.

## Epistemic status and boundaries

Observed here: raw SAPA availability, marginal item response rates, the deterministic greedy nested item order, strict joint complete-case counts, and relaxed coverage counts. Interpretation is limited to possible regions of sharper coverage loss. Unknowns include the eventual panel size, respondent cohort, partial-profile method, human/model common features, and whether any later human grouping corresponds to model personas.

No construct scores (including the 126 named psychological constructs), imputation, PCA, IRT, FIML, matrix completion, clustering, human/model matching, model PCA, specificity analysis, model inference, activation extraction, external model API, GPU, or RunPod were used. Track 1 remains active; Tracks 2 and 3 remain parked. The next decision is to inspect this frontier and decide what dimensionality/sample-size region is scientifically worth considering—not to begin clustering.
