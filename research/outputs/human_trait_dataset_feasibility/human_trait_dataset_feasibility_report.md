# Phase 1 human-data feasibility: SAPA trait vocabulary and NLSY97 occupation/outcome audit

**Status:** active feasibility result

**Generated:** 2026-09-11

**Scope:** data acquisition, measurement coverage, co-observation, and occupational cell sizes only

## Executive answer

Phase 1 supports a deliberately limited next experiment, but not a general human-to-model projection. SAPA supplies face-valid direct or close content for 127 of the project's 240 activation-derived trait labels, while 113 labels have only broad-domain or no defensible coverage. NLSY97 supplies a large same-wave Round-12 personality/occupation sample (6,261 respondents), but its TIPI measurement is much narrower and most individually mapped persona occupations are sparse: only 2 of 98 translated persona-role rows reach N>=100, and both refer to the same secretary/administrative-assistant occupation cell.

The justified next step is a preregistered measurement-bridge design restricted to SAPA constructs with category 3 evidence, followed by a small set of occupation comparisons that are fixed in advance and have adequate NLSY97 cells. This audit does **not** establish construct equivalence, does not assign LLM persona labels to humans, and does not project any human respondent into Qwen geometry.

## Provenance and boundaries

| Component | Source and use |
|---|---|
| Model trait vocabulary | Canonical 240 names and definitions from `data/traits/trait_list.json` |
| Prior occupation judgments | `research/outputs/occupation_population_persona_join/role_occupation_mapping.csv`; its exact/close/broad/ambiguous/no-match distinctions were retained |
| SAPA | [Harvard Dataverse DOI 10.7910/DVN/SD7SVE](https://doi.org/10.7910/DVN/SD7SVE), V5, CC0 1.0 |
| SAPA documentation | [Data paper, DOI 10.5334/jopd.al](https://doi.org/10.5334/jopd.al), Dataverse metadata, release item/scale files, and bundled update paper |
| NLSY97 | [Official BLS cohort page](https://www.bls.gov/nls/nlsy97.htm) and an official [NLS Investigator](https://www.nlsinfo.org/investigator/pages/search) public-use guest extraction |
| NLSY97 documentation | Extract-specific Investigator codebook plus official topical guides for [attitudes/noncognitive measures](https://www.nlsinfo.org/content/cohorts/nlsy97/topical-guide/attitudes/attitude-and-noncognitive-skills-measures), [occupation](https://www.nlsinfo.org/content/cohorts/nlsy97/topical-guide/employment/occupation), and [sample weights/design](https://www.nlsinfo.org/content/cohorts/nlsy97/using-and-understanding-the-data/sample-weights-design-effects) |
| Occupation classification | Official [2002 Census occupation code list with 2000 SOC links](https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2002-census-occupation-codes.xls) and [BLS 2010-to-2018 SOC crosswalk/manual](https://www.bls.gov/soc/2018/crosswalks.htm); official-crosswalk stable codes, exact normalized titles, and explicit title-reviewed older-frame translations only |
| New model inference | None |

Respondent-level files reside only under gitignored `data_external/human_validation/`. Committed artifacts contain dictionaries, manifests, crosswalk judgments, aggregate cell counts, and whole-sample overlap counts. No row-level criminal-justice record or occupation-specific justice outcome was emitted.

## Observed

### SAPA release and integrity

The acquired release is **Selected personality data from the SAPA-Project: 08Dec2013 to 26Jul2014**, Harvard Dataverse V5, persistent identifier `doi:10.7910/DVN/SD7SVE`, released as V5 on 2025-03-23 and downloaded on 2026-09-11. The actual tab file contains **23,679 respondents, 719 columns, and 696 unique psychological items**. The remaining 23 columns are identifiers, demographics, and derived demographic/employment fields, including age, gender, education, job status, occupational prestige, and estimated occupational income.

The release item metadata identifies **92 administered source constructs**: IPIP100 (5), Big Five Aspect Scales (10), HEXACO (24), Questionnaire Big Six (6), MPQ (12), IPIP-NEO (30), EPQ-R (3), and plasticity/stability (2). `superKey696.csv` separately provides **131 derived scoring keys**; these are not an additional 131 administered scales. Responses use 1=Very Inaccurate through 6=Very Accurate, with reverse keying preserved in the item and scale inventories.

There are two documented discrepancies. The data-paper abstract reports 23,681 observations, whereas the V5 tab file and the bundled update paper yield/report 23,679. The release's demographic code file says items begin after 20 columns, but the actual tab file has 23 non-item columns. All 696 response columns align exactly with the release item dictionary.

### SAPA planned missingness

SAPA's random-subset administration is evident in the response matrix:

| Quantity | Verified value |
|---|---:|
| Mean answered items/respondent | 86.144 of 696 (12.38%) |
| Median answered items/respondent | 71 |
| 5th–95th percentile | 36–295 |
| Minimum–maximum | 0–311 |
| Mean respondents/item | 2,930.8 |
| Median respondents/item | 2,554 |
| Minimum–maximum respondents/item | 2,304–6,096 |
| Overall empty item-cell fraction | 87.62% |

The release does not supply a cell-level flag separating planned nonadministration from ordinary nonresponse, so an exact planned-versus-unplanned decomposition is not available. The empty-cell rate must not be interpreted as conventional item nonresponse.

### SAPA coverage of the 240 model traits

Candidate generation used exact-token and deterministic lemma-like overlap followed by repository-local word and character TF-IDF. Codex then reviewed exact item wording against the canonical model-trait definition. This third stage is a documented feasibility judgment, **not independent psychometric validation**.

| Coverage category | Model traits | Share |
|---|---:|---:|
| 3 — direct / near-direct construct coverage | 78 | 32.5% |
| 2 — close narrow construct | 49 | 20.4% |
| Category >=2 | 127 | 52.9% |
| 1 — broad-domain only | 41 | 17.1% |
| 0 — no defensible coverage found | 72 | 30.0% |

The 78 direct traits use 131 distinct accepted SAPA items and 82 source-scale labels. Expanding to categories 2–3 uses 180 distinct items and 89 source-scale labels. Every accepted match retains item IDs, exact evidence text, scale membership, direction, ambiguity status, and candidate alternatives in `sapa_model_trait_candidate_crosswalk.csv`.

Coverage is strongest for ordinary affective, interpersonal, and self-regulatory constructs: anxiety/calm, pessimism/optimism, sociability/reserve, agreeableness/hostility, conscientiousness/disorganization, risk taking, impulsivity, dominance/submission, empathy/altruism, and conventionality/openness. Several socially undesirable constructs have narrow item evidence—such as manipulative, cruel, vindictive, callous, and hostile—so the inventory is not limited to socially desirable Big Five content.

Coverage is weakest for response style and rhetoric (`verbose`, `literal`, `metaphorical`, `narrative`, `rhetorical`, `cryptic`), epistemic/methodological stance (`data_driven`, `reductionist`, `constructivist`), philosophical or political doctrine (`utilitarian`, `deontological`, `libertarian`, `relativist`), and symbolic/aesthetic discourse modes (`poetic`, `ethereal`, `esoteric`). Many cognitive or communication labels have only broad-domain evidence. The audit did not force these labels into Big Five bins.

### NLSY97 public-data acquisition

**ACCESS OBTAINED.** The official NLS Investigator guest workflow produced a public-use NLSY97 1997–2023 (Rounds 1–21) extract containing all **8,984 original cohort respondents** and 126 selected columns. No account, CAPTCHA bypass, or circumvention was used. Restricted geocodes were neither requested nor obtained.

The personality manifest contains:

- Round 12 (2008): all **10 raw TIPI items** (`T3162500`–`T3162509`), their 1–7 response scale, construct pairs, and reverse-scoring directions.
- Round 6 (2002): all **8 Goldberg Agreeableness/Conscientiousness bipolar items** (`S0920000`–`S0920700`) and their 1–5 anchors/directions. Their universe was respondents age <=14 at the end of 1996, so they do not cover the full cohort.
- Round 12: four industriousness and four traditionalism items.
- Round 16: eight Short Grit Scale items; Round 17: the eight-item repeat for specified Round-16 nonrespondents.

### NLSY97 occupation measurement and same-wave counts

Round-12 and Round-6 primary occupations use **four-digit 2002 Census occupation codes derived from 2000 SOC**. The analysis first reads the same-round `CV_MAINJOB_FLG` and then selects the matching roster-loop `YEMP_OCCODE-2002.xx`; it never assumes roster loop 1. The manifest also retains industry, employment status context, class of worker, job tenure, freelance/contractor variables, military-employer flags, and survey-design fields.

| Feasibility sample | Unweighted N |
|---|---:|
| Original cohort | 8,984 |
| Round-12 TIPI all ten complete | 7,044 |
| Round-12 TIPI complete + valid same-wave occupation | 6,261 |
| Round-6 Goldberg all eight complete | 4,851 |
| Round-6 Goldberg complete + valid same-wave occupation | 4,060 |

The Round-12 cumulative-cases weight gives a descriptive population estimate of 16,499,071.2 for the primary sample. It is reported separately from raw N and was not used for inferential testing.

### Persona-role occupation cells

The prior repository mapping supplied 98 persona roles marked for occupational analysis. Translation to the older NLSY97 code frame used 37 official-crosswalk stable SOC-code matches, 6 exact normalized-title matches, and 55 explicit title-reviewed mappings to an official 2002 Census category. A stable code had to remain unchanged through the official BLS 2010-to-2018 SOC crosswalk and appear in the official 2002 Census list's 2000-SOC column; split/merge cases such as `51-9199` were handled as title-reviewed older-frame mappings instead. The original exact/close/broad match class remains visible on every row; no previously excluded or unmatched persona was promoted merely to make a larger cell.

Feasibility thresholds count **persona-role mapping rows**, not statistically independent occupations, because multiple persona labels sometimes share one Census cell:

| Round-12 cell label | Persona-role rows | Unique Census code sets |
|---|---:|---:|
| Strong, N>=100 | 2 | 1 |
| Moderate, 50<=N<100 | 5 | 4 |
| Exploratory, 20<=N<50 | 20 | 12 |
| Too sparse, N<20 | 71 | 50 |

The only strong cell is Secretaries and administrative assistants (N=113), shared by `secretary` (prior exact match) and `assistant` (prior broad match). Moderate cells include construction laborers for `builder` (N=87), accountants/auditors for `accountant` and `auditor` (N=59), personal/home-care aides for `caregiver` (N=59), and other production workers for `artisan` (N=54). Useful exploratory examples include wholesale/manufacturing sales for `merchant` (N=48), office-support supervisors (N=47), automotive mechanics (N=45), counselors (N=44), training/HR specialists (N=43), designers (N=29), and other teachers/instructors (N=24).

Many substantively attractive exact or close mappings are too sparse: lawyer N=17, programmer N=13, journalist N=9, writer N=8, generic engineer N=7, therapist N=7, psychologist N=3, actor N=0, and the narrow enlisted tactical military code N=0. These cells were not broadened after observing N.

### NLSY97 longitudinal outcome inventory and overlap

The machine-readable outcome inventory verifies public-use families for education, earnings/income, employment histories, unemployment spells, job tenure, marriage/family, health, mental health, substance use, risk behavior, crime/delinquency, arrest and justice histories, incarceration, military service, and civic/community participation. Availability does not imply that every series was extracted; exact extracted probes and broader documented series are distinguished row by row.

Within the 6,261-person Round-12 personality + occupation sample, observed later-wave probe counts are:

| Later domain probe | Co-observed N |
|---|---:|
| Employment (weeks worked in 2009) | 6,178 |
| Education (highest grade, Round 13) | 6,007 |
| Justice (Round-13 arrest item) | 6,021 |
| General health (Round 13) | 6,049 |
| Substance use (days smoked, conditional follow-up) | 2,322 |
| Family income (Round 13) | 5,379 |
| Marital status (Round 13) | 6,040 |

The lower smoking overlap reflects its conditional item universe and must not be treated as generic attrition. Justice information is handled only as longitudinal outcome metadata plus this whole-sample availability count; no criminal-personality score, respondent label, or subgroup justice table was created.

### Survey design

NLSY97 combines a cross-sectional sample and a supplemental oversample. The extract retains `CV_SAMPLE_TYPE` (`R1235800`), Round-12 cumulative-cases sampling weight `T2022500` (two implied decimals), stratum `VSTRAT` (`R1489700`), and PSU `VPSU` (`R1489800`). Raw N is the sole basis for feasibility labels. Any later population inference must use the appropriate wave/analysis weight with strata and PSUs; simple-random-sample standard errors would be inappropriate.

## Inferred

SAPA is rich enough to justify designing a **restricted** human/model measurement bridge. The case is strongest for the 78 category-3 labels and perhaps a preregistered subset of category-2 labels after independent review. It is not rich enough to treat the full 240-dimensional model vocabulary as a measured human trait battery, because 47.1% of labels have only broad or no defensible content and the crosswalk has not undergone psychometric validation.

SAPA planned missingness is severe at the respondent-by-item level but not inherently disqualifying: each item still has at least 2,304 respondents. A later analysis would need design-aware missing-data and scoring decisions and should avoid assuming every respondent has a complete narrow-trait profile.

NLSY97 is adequate for a small number of occupation-group feasibility comparisons using TIPI or the limited Round-6 Goldberg dimensions. It is not adequate for broad testing of many narrow occupational prototypes one by one. The strongest cells are often broad or shared mappings, while many appealing exact occupational labels remain below N=20. NLSY97 therefore complements SAPA's vocabulary breadth with longitudinal outcomes and occupation histories; it does not replace SAPA as a 240-trait measurement source.

Proceeding is justified only as a staged design exercise: freeze independently defensible trait correspondences, choose a small set of occupation categories based on mapping quality and predeclared N thresholds, and specify measurement/inference rules before any model-geometry comparison. No conclusion about correspondence is supported by this audit alone.

## Unknown

- Whether the Codex-reviewed SAPA category-3 and category-2 links survive independent expert review, factor analysis, reliability checks, measurement-invariance checks, and preregistration.
- Whether enough jointly administered SAPA item content exists per respondent to score every proposed narrow bridge construct without an inappropriate missing-data model.
- Whether human occupation-group trait distributions correspond to LLM role prototypes. This was deliberately not tested.
- Whether a defensible bridge should use scale scores, item-response models, latent factors, or another representation. No mapping model was fit here.
- Whether sparse NLSY97 roles can be pooled without changing the scientific construct. No post hoc broadening is authorized by this audit.
- Which restricted NLSY97 variables, if any, would add enough value to justify a separate application. Public-use data were sufficient for the present audit; restricted geocodes were not accessed.

## Single most useful next research task

Conduct an independent, blinded review of the 78 category-3 SAPA links using the preserved canonical trait definitions, exact SAPA item text, scoring keys, and scale memberships. The output should freeze a smaller construct set and rejection reasons **before** any human-to-model geometry or occupation comparison is attempted.

## Reproduction

```bash
PYTHON=/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/.venv/bin/python

$PYTHON research/outputs/human_trait_dataset_feasibility/scripts/audit_sapa_trait_coverage.py \
  --raw-dir data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE \
  --traits data/traits/trait_list.json \
  --output-dir research/outputs/human_trait_dataset_feasibility/sapa

$PYTHON research/outputs/human_trait_dataset_feasibility/scripts/audit_nlsy97_feasibility.py \
  --raw-dir data_external/human_validation/nlsy97/public_use_extract \
  --occupation-xls data_external/human_validation/nlsy97/occupation_crosswalks/2002-census-occupation-codes.xls \
  --prior-crosswalk research/outputs/occupation_population_persona_join/role_occupation_mapping.csv \
  --output-dir research/outputs/human_trait_dataset_feasibility/nlsy97

$PYTHON research/outputs/human_trait_dataset_feasibility/scripts/verify_human_dataset_feasibility.py \
  --repo-root . --write-inventory

$PYTHON research/outputs/human_trait_dataset_feasibility/scripts/verify_human_dataset_feasibility.py \
  --repo-root . --check-only
```

These scripts are CPU-only and make no model or external LLM API calls. Source manifests record local file paths, sizes, SHA256 hashes, access terms, and canonical institutional URLs. The artifact inventory records hashes and canonical raw GitHub URLs for every committed analysis artifact.

## Prohibited analyses confirmation

- No respondent-level human microdata were committed.
- No human respondent was assigned an LLM persona label.
- No SAPA or NLSY97 respondent was projected into Qwen PCA space.
- No human-to-model trait regression, occupational centroid, or correspondence test was run.
- No GPU, RunPod, model inference, activation extraction, or external model API was used.
