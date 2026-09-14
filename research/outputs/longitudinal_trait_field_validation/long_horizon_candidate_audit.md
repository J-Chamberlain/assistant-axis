# Long-Horizon Candidate Cohort Audit

Status: active, outcome-blind measurement/access audit under the frozen multi-cohort longitudinal harmonization protocol.

Date: 2026-09-14.

Branch: `gpt/longitudinal-trait-field-validation`.

Protocol dependency: `multi_cohort_longitudinal_harmonization_protocol_freeze.md`, frozen before this audit and before participant-level longitudinal lower-level outcomes in HILDA, HRS, MIDUS, SOEP, or LISS were inspected for this project.

## Bottom line

The long-horizon program is feasible in more than one cohort, but the cohorts are not interchangeable. LISS currently offers the strongest combination of repeated measurement frequency and lower-level item richness. HRS offers a strong second design with a stable 26-item common adjective core over repeated four-year intervals in two rotating subsamples. HILDA offers a 16-year nationally representative panel with a relatively rich adjective battery. MIDUS offers an unusually long approximately 19-year span and a rich 25-adjective MIDI battery, but its current data-use terms explicitly prohibit uploading MIDUS data to public large-language-model or AI platforms. SOEP offers a large 12-year core panel and clean repeated item wording, but its 15-item BFI-S is much thinner and is best treated as a lower-resolution replication.

Published longitudinal measurement-invariance results are not fully uniform across analytic frameworks. One HILDA age-trajectory analysis found metric but not scalar invariance, especially for Openness and Agreeableness, whereas another multi-panel repeated-measures analysis reported acceptable invariance under its criteria for HILDA and LISS and near-acceptable exceptions in SOEP/HRS. This disagreement strengthens rather than removes the frozen requirement for a project-specific invariance gate on the exact item sets used by each bridge. No cohort is promoted to M1 merely from the literature review.

No participant-level longitudinal target outcomes were inspected in constructing the bridges below. The bridge judgments use source documentation, exact item wording, published measurement information, and the already-frozen BFI-2 facet vocabulary only.

## Candidate ranking before outcome analysis

### 1. LISS: highest-priority scientific target

Observed source structure: the LISS Core Study Personality questionnaire uses the 50-item IPIP Big Five inventory. Public archive pages show the same item sequence from Wave 1 in 2008 through recent waves, including Wave 16 in 2024, Wave 17 in 2025, and Wave 18 in 2026. The current Wave 18 page labels this the eighteenth Personality wave. The archive provides an encrypted stable respondent identifier for longitudinal merging. Published coordinated analyses report 16 personality waves from 2008 through 2024, while the archive now contains later waves as well.

The item set is unusually favorable for the frozen bridge. Strong lower-level mappings are available for Sociability; Compassion, Respectfulness and Trust; Organization, Productiveness and Responsibility; Anxiety, Depression and Emotional Volatility; and Intellectual Curiosity and Creative Imagination. Aesthetic Sensitivity has no clean IPIP-50 counterpart, while Assertiveness and Energy Level are weaker semantic proxies rather than primary matches. This produces 12 primary DIRECT/CLOSE candidate facets across all five broad domains, above the frozen HIGH-COVERAGE threshold.

Leakage is manageable because each Big Five domain has ten IPIP items. Target-specific leave-out broad scores can retain multiple independent indicators after removing the lower-level target items.

Measurement status: repeated item wording is highly favorable. Published invariance analyses differ somewhat in modeling choices and conclusions, with at least one recent repeated-measures analysis reporting satisfactory invariance across LISS waves. The current project nevertheless does not assign M1 from those studies because our target-specific leave-out scores and lower-level bridge are not identical to the published measurement models. Project-specific longitudinal scalar or partial-scalar tests on the exact bridge item sets remain a required pre-outcome gate.

Known wave issues: some published analyses describe planned-missingness/full-sample differences across LISS personality waves. These are design/coverage issues, not reasons to select favorable intervals. Every compatible interval must be enumerated before outcomes are inspected.

Access boundary: LISS datasets require a signed user statement. Centerdata states that access is personal and that users may not make copies of the data available to others. Raw LISS respondent data therefore should not be uploaded into this ChatGPT thread without explicit permission from Centerdata. The practical path is a local runner executed by an authorized user, with only permitted aggregate outputs brought back for synthesis.

Provisional status: `HIGH-COVERAGE; exact-bridge measurement gate pending; local execution required by current access terms`.

## 2. HRS: high-priority replication target

Observed source structure: the HRS Psychosocial and Lifestyle Questionnaire contains the MIDI personality adjectives. The official cross-wave concordance documents a stable 26-item common core while additional items were introduced later. A recent harmonized longitudinal source lists HRS-A personality waves in 2006, 2010, 2014, 2018, and 2022 and HRS-B waves in 2008, 2012, 2016, and 2020. The common 26 items therefore support repeated four-year intervals and long-horizon analyses in two rotating subsamples.

The common adjective set supports strong lower-level candidates for Sociability and Energy Level; Compassion; Organization, Productiveness and Responsibility; Anxiety and Emotional Volatility; and Intellectual Curiosity and Creative Imagination. Assertiveness, Respectfulness, Trust, Depression, and Aesthetic Sensitivity do not have clean common-item counterparts. This yields 10 primary DIRECT/CLOSE candidate facets across all five domains, meeting the HIGH-COVERAGE threshold.

Leakage is manageable by target-specific leave-out scoring. For example, Sociability can use Outgoing/Talkative while the broad Extraversion score retains Friendly/Lively/Active; Anxiety can use Worrying/Nervous while the broad emotional-instability score retains Moody/Calm; Conscientiousness has sufficient common items to separate Organization, Productiveness, and Responsibility targets one at a time.

Measurement status: exact wording is documented across waves, and published multi-panel work has reported broadly acceptable longitudinal invariance under its criteria, with some model-specific exceptions. Because that model is not identical to the exact common-26 leave-target-out bridge here, HRS remains an M2 candidate pending the project-specific measurement gate rather than being assumed M1.

Population boundary: HRS primarily represents older U.S. adults rather than the full adult age range. That makes it a valuable age/context replication, not a substitute for a general-population cohort.

Access boundary: HRS public-release files require individual registration. The official Conditions of Use prohibit transfer of HRS data to third parties except under specified institutional arrangements, and HRS announced an updated AI/LLM policy in 2026. Raw HRS data should not be uploaded into this ChatGPT thread unless the current agreement explicitly permits that processing. Use an authorized local execution path and return only permitted aggregate results.

Provisional status: `HIGH-COVERAGE; M2 candidate pending exact-bridge invariance audit; local execution required by current access terms`.

## 3. HILDA: strong long-horizon population cohort with measurement caveat

Observed source structure: HILDA administers a 36-adjective Big Five battery derived largely from Saucier/Goldberg markers. The standard HILDA broad scales use 28 recommended items. Recent coordinated work identifies personality assessments in 2005, 2009, 2013, 2017, and 2021, giving a 16-year span. Earlier HILDA documentation records the item wording and the 28-item scoring set.

The bridge can support strong or plausible lower-level targets for Sociability and Energy Level; Compassion and Respectfulness; Organization, Productiveness and Responsibility; Anxiety and Emotional Volatility; and Intellectual Curiosity and Creative Imagination. Depression, Trust, Assertiveness, and Aesthetic Sensitivity do not have clean mappings. Two potentially useful target indicators, Harsh for Respectfulness and Careless for Responsibility, are among the eight adjectives not retained in the standard 28-item broad scales because of factor/cross-loading concerns. They remain semantically CLOSE but are not eligible for primary use unless the preregistered baseline psychometric gate passes. HILDA therefore has 9 robust candidate facets and up to 11 eligible facets after that pre-outcome gate. It is guaranteed MULTI-DOMAIN ELIGIBLE and may become HIGH-COVERAGE.

Leakage is manageable because the broad scales contain four to six items per domain and the excluded adjectives create target-only evidence. Every target must use a target-specific leave-out broad score where overlap remains.

Measurement status is the central issue. One detailed HILDA longitudinal analysis over 2005, 2009, 2013, and 2017 found metric invariance but reported that scalar invariance could not be established, especially for Openness and Agreeableness. Other repeated-measures work using different modeling choices has reported acceptable invariance. Under the frozen protocol, this mixed literature means HILDA cannot be assumed M1. The exact lower-level bridge and leave-out broad item sets require project-specific scalar/partial-scalar tests before outcome analysis. Failure of that gate downgrades affected intervals/facets rather than triggering remapping.

Access boundary: HILDA unit-record data require an approved DSS/ADA application and a signed Confidentiality Deed Poll. The default assumption is that raw HILDA microdata should remain in the authorized local environment unless the applicable agreement expressly permits external processing. The practical path is local execution and aggregate export.

Provisional status: `MULTI-DOMAIN guaranteed; possible HIGH-COVERAGE; exact-bridge measurement gate required; local execution`.

## 4. MIDUS: scientifically strong, operationally local-only

Observed source structure: MIDUS measures the Big Five with the 25-item Midlife Development Inventory adjective battery. The main longitudinal waves are approximately 1995-1996, 2004-2006, and 2013-2014, spanning roughly 19 years. The personality item set closely parallels the HRS common MIDI items, with 4 Neuroticism, 5 Extraversion, 7 Openness, 5 Agreeableness, and 4 Conscientiousness adjectives.

The bridge therefore supports approximately the same ten canonical facets as HRS: Sociability, Energy Level, Compassion, Organization, Productiveness, Responsibility, Anxiety, Emotional Volatility, Intellectual Curiosity, and Creative Imagination. It meets the HIGH-COVERAGE threshold across five domains. Target-specific leave-out scoring remains feasible even with only four Conscientiousness and four Neuroticism items because each target is tested separately and at least two nonoverlapping broad indicators can remain for the proposed primary mappings.

Measurement status: published work supports the MIDI's broad factorial structure, but this audit did not establish a longitudinal scalar-invariance result for the exact three-wave leave-target-out bridge. The cohort remains M2-candidate pending a project-specific wave-invariance audit.

Access boundary: MIDUS explicitly states that users must not upload MIDUS data to public large-language-model or AI platforms including ChatGPT, Claude, Gemini, and Copilot. Therefore participant-level MIDUS analysis cannot be performed in this chat. A local non-AI analysis runner is required.

Provisional status: `HIGH-COVERAGE; M2 candidate pending longitudinal invariance; mandatory local non-AI execution`.

## 5. SOEP: useful thinner replication

Observed source structure: SOEP uses the BFI-S, with three items per Big Five domain in 2005, 2009, 2013, and 2017. A fourth Openness item, eager for knowledge, was added from 2009 onward. The core repeated items use stable seven-point wording.

The short battery still supports a meaningful lower-level bridge if each target uses a single highly specific source item and the broad predictor uses the two remaining same-domain indicators. Candidate primary facets are Sociability; Compassion and Respectfulness; Productiveness and Responsibility; Anxiety; Aesthetic Sensitivity and Creative Imagination; and, from 2009 onward, Intellectual Curiosity. This yields about eight primary facets for the 2005-2017 common-item span and about nine for 2009-2017, spanning all five broad domains. It therefore meets MULTI-DOMAIN ELIGIBLE but not HIGH-COVERAGE.

The design is more fragile than LISS/HRS/HILDA/MIDUS because each broad domain has only three items. A two-item lower-level target would leave only one broad predictor indicator and become ineligible under the frozen leakage rule, so the primary bridge must remain single-item at the lower level. That increases measurement noise and makes this cohort more useful as replication than as a flagship test.

Measurement status: the literature includes both support for longitudinal measurement invariance under some designs and evidence of scalar-invariance strain under others. Because the source instrument is so short and our leave-target-out predictors differ from published full-domain models, SOEP is not presumed M1. Project-specific partial-scalar tests on the exact single-item targets and two-item broad scores are required. The 2005 absence of the fourth Openness item is handled by retaining the common three-item broad Openness definition across the long 2005-2017 interval; Intellectual Curiosity is simply unavailable for that interval rather than changing the broad coordinate definition.

Access boundary: SOEP scientific-use microdata are distributed under a user/data contract. Exact current third-party/cloud-processing permissions must be checked before any participant-level file is provided to an external system. Default plan: local execution until the agreement is reviewed.

Provisional status: `MULTI-DOMAIN ELIGIBLE; lower-resolution replication; exact-bridge measurement gate required; local execution by default`.

## Outcome-blind bridge summary

The current bridge audit supports the following expected primary facet counts before baseline psychometric/invariance gates:

- LISS: 12 facets across 5 domains, HIGH-COVERAGE.
- HRS: 10 facets across 5 domains, HIGH-COVERAGE.
- HILDA: 9 robust facets, up to 11 after two pre-outcome psychometric gates, across 5 domains; MULTI-DOMAIN guaranteed, possible HIGH-COVERAGE.
- MIDUS: 10 facets across 5 domains, HIGH-COVERAGE.
- SOEP: approximately 8 facets across 5 domains for the 2005-2017 common-item span; 9 from 2009 onward; MULTI-DOMAIN.

These counts are semantic/measurement feasibility results, not longitudinal findings. No result may be upgraded after change outcomes are visible.

## Recommended execution order

The scientific order is LISS first, then HRS, HILDA, MIDUS, and SOEP, with PEACH retained as the already-partially-inspected intervention/short-horizon secondary test. This order is based on bridge coverage, wave frequency, time span, measurement richness, and population complementarity, not outcome performance.

The operational order may differ because raw microdata access agreements generally prevent or constrain uploading these datasets directly into ChatGPT. The next implementation task should therefore be a single local, non-networked harmonization runner that consumes dataset-specific source files plus frozen bridge manifests, performs only the predeclared measurement gate and longitudinal tests, and exports privacy-safe aggregate CSV/JSON outputs. The same runner should be used across cohorts wherever possible.

## Findings, interpretations, unknowns

Observed: each of the five long-horizon cohorts contains enough repeated personality information to support at least a multi-domain test under the frozen vocabulary. LISS, HRS, and MIDUS have enough lower-level item richness for HIGH-COVERAGE candidate bridges before psychometric gates; HILDA may also reach HIGH-COVERAGE. Data-use restrictions prevent treating these public or registered datasets as freely redistributable files.

Interpretation: the multi-cohort program is substantially stronger than a PEACH-only design because it can test the same directional prediction across different countries, age structures, time intervals, and measurement instruments.

Unknown: exact eligible person-interval N, project-specific scalar/partial-scalar invariance, baseline coherence of marginal HILDA mappings, attrition effects, and final DIRECT/CLOSE counts cannot be known until authorized microdata are processed locally. Published invariance studies use measurement models that are not identical to our target-specific bridge, so they cannot substitute for the frozen project-specific gate. None of these gates may be relaxed based on longitudinal prediction performance.

## Principal external sources consulted

HILDA: Melbourne Institute HILDA personality documentation and statistical reports; Losoncz HILDA personality-scale development; recent coordinated HILDA/HRS/LISS personality-wave summaries; Seifert et al. longitudinal measurement-invariance analyses; DSS data-access guidance.

HRS: official HRS Psychosocial and Lifestyle Questionnaire 2006-2022 user guide and cross-wave concordance; HRS public-data Conditions of Use and 2026 AI/LLM policy announcement.

LISS: Centerdata LISS Data Archive Wave 1 and recent Personality wave pages; Centerdata data-use rules; published longitudinal LISS measurement-invariance analyses.

SOEP: SOEPcompanion Big Five documentation and BFI-S item wording; published longitudinal measurement-invariance analyses.

MIDUS: MIDUS/ICPSR current data-use and AI policy; published MIDI psychometric work and three-wave longitudinal descriptions.
