# SAPA Static Human Terrain Analysis Specification

Status: PRE-RESULT METHOD SPECIFICATION

Date: 2026-09-13

Branch: `gpt/sapa-static-human-terrain`

## Purpose

The purpose of this analysis is to characterize the static occupancy topology of human personality space in the SAPA V5 sample before any comparison with model persona geometry. The target object is a continuous five-dimensional human personality terrain rather than a discrete personality taxonomy. The analysis asks where human profiles are densely or sparsely represented, whether high-density regions remain connected as density thresholds rise, whether reproducible bottlenecks or alternative corridors exist, and whether any apparent topology exceeds what is expected from simpler distributions with the same broad marginal and covariance structure.

This analysis is explicitly static. Density, ridges, holes, bottlenecks, and corridors are occupancy features. They must not be described as attractors, transition probabilities, barriers to change, or paths of least resistance without longitudinal evidence.

## Source and representation

The primary dataset is Harvard Dataverse SAPA V5, DOI `10.7910/DVN/SD7SVE`, previously verified in this project at 23,679 retained respondent rows, 696 psychological items, and 2,039,803 observed behavioral response cells. Raw respondent data remain uncommitted and gitignored.

The primary coordinate system is the Big Five. The exact five-domain scoring key will be taken from the official SAPA release and frozen before terrain analysis. If more than one official five-domain key is present, the pre-result preference order is a published official domain key with explicit item membership and scoring direction, with IPIP100 used as the primary key if present and other official five-domain keys retained as sensitivity representations.

The analysis architecture is dimension-agnostic. The same terrain pipeline must accept an `N x D` respondent-coordinate matrix. Five dimensions are primary because they provide the standard psychological coordinate system and make continuous topology estimable at the available sample size. Richer representations such as aspects, facets, or narrower trait systems are later resolution analyses, not post hoc replacements chosen because the Big Five terrain is visually uninteresting.

## Planned-missingness scoring problem

SAPA used planned random-subset administration. Earlier project work showed that broad latent profile structure can be recovered directly from observed partial responses and that administration-mask diagnostics are near chance, but it did not validate deterministic completion of each respondent's missing item responses. This analysis therefore does not impute missing questionnaire answers and then pretend they were observed.

The scoring stage will compare respondent-coordinate estimators before any terrain result is inspected. Method choice will be based on recovery and calibration diagnostics, never on which method produces more interesting terrain.

The baseline estimator is the official-key available-item score. Items are reverse-scored according to the official key, standardized using training-split item moments, and aggregated only over items actually answered by that respondent. This estimator is transparent and does not impose a global population-shape prior, but it can be noisy when domain coverage is sparse.

The principal candidate estimator is an anchored all-item factor-regression score. A five-factor loading system is estimated from human SAPA item covariance using only training data. The factor orientation is anchored to the official Big Five key rather than selected from model geometry. Respondent scores are then estimated from the subset of items actually observed for each respondent using weighted least squares or an equivalent missingness-aware factor-score equation. The estimator must not assume a multivariate-normal respondent prior whose shape would itself force the downstream terrain toward a Gaussian cloud. Any regularization must be documented and evaluated for shrinkage-induced topology distortion.

If a stable ordinal item-response implementation is computationally feasible, an ordinal missingness-aware score may be evaluated as a secondary candidate. It cannot become primary merely because its terrain appears cleaner. A latent population prior that predetermines unimodality or a small finite mixture is not acceptable as the primary scoring model for a topology study.

## Scoring-method validation and freeze

Coordinate scoring is validated before terrain estimation. The primary diagnostics are held-out observed-item prediction, artificial-mask stability, domain rank preservation, score RMSE under masking relative to the respondent's higher-coverage estimate, and uncertainty calibration where the estimator supplies uncertainty.

Artificial masking will use administration patterns sampled from the empirical SAPA missingness process. Higher-coverage respondents provide the reference observations for this validation, but their reference scores are treated as higher-information estimates rather than ground truth. Results must be stratified by number of answered items and by domain coverage.

The scoring method, coverage eligibility rule, standardization procedure, and all regularization parameters are frozen after this validation and before any density, mode, corridor, bottleneck, or topology result is inspected.

A scoring method is rejected if score recovery degrades sharply at typical SAPA coverage, if missingness pattern predicts coordinates after conditioning on response count, or if the method creates strong central shrinkage that is not reproduced in higher-coverage respondents.

## Primary static terrain

All five primary Big Five coordinates are standardized within the human sample using the frozen scoring procedure. The primary density estimator is adaptive k-nearest-neighbor density in five dimensions. The neighbor count is selected by a predeclared stability rule using held-out likelihood or nearest-neighbor density stability, not by visual preference. Fixed-bandwidth Gaussian KDE is a sensitivity analysis rather than the sole primary estimator.

The terrain is summarized across density superlevel sets. At a sequence of frozen density quantiles, respondents form a mutual or symmetric k-nearest-neighbor graph restricted to points above the threshold. Connected components are tracked across thresholds to form a cluster tree. The primary outputs are the number and persistence of connected high-density regions, merge thresholds, component mass, and the stability of these features across independent data splits.

Modes are local density maxima that persist across a minimum range of density thresholds and recur across split-half fits. A mode is not automatically a personality type.

A corridor between two persistent modes is defined graph-theoretically. The primary corridor score is the widest-path or maximum-bottleneck path through the respondent neighborhood graph, where path quality is determined by the minimum density encountered along the path. The bottleneck value is reported relative to the endpoint-mode densities and to null distributions. This is a static support corridor only. It is not a transition pathway.

Potential holes and loops are secondary topology features. Persistent homology may be run on a computationally tractable landmark or witness representation, with H0 and H1 emphasized. Any hole claim requires persistence beyond bootstrap and split-sample null expectations. A visually empty patch in a projection is not evidence of a high-dimensional hole.

Local intrinsic dimensionality and local covariance anisotropy are secondary diagnostics used to identify whether different regions of Big Five space behave like locally lower-dimensional sheets, tubes, or broader volumes. These diagnostics are descriptive and cannot establish dynamical constraints.

## Null models

Observed topology is compared with at least three frozen null families. The first is a multivariate Gaussian matching the observed mean and covariance. The second is a Gaussian-copula null that approximately preserves each empirical marginal distribution and the broad rank-correlation structure while removing higher-order dependence. The third independently permutes respondent coordinates within each Big Five domain, preserving univariate marginals while destroying cross-domain dependence.

The Gaussian-copula null is the primary structural null because it preserves much of the broad one-dimensional and pairwise structure while removing nonlinear higher-order organization. The independent-permutation null is intentionally weaker and is reported as such.

For each null family, the full terrain pipeline is repeated with the same sample size and scoring-coordinate scale. Comparisons include mode persistence, superlevel-set component counts, merge thresholds, maximum corridor bottleneck scores, H1 persistence where computed, and local-density heterogeneity.

## Measurement uncertainty

Terrain results must be tested for sensitivity to respondent-coordinate uncertainty. The preferred implementation uses repeated coordinate perturbations or resampling derived from the frozen scoring model's empirical masking error or score uncertainty. The goal is to determine whether major terrain features survive plausible scoring noise.

Uncertainty propagation must not use a prior distribution that imports the topology being tested. If only empirical masking errors are available, those errors are the primary perturbation source.

## Replication and stability

The primary sample is split deterministically into two independent halves before terrain fitting. The full terrain pipeline is run separately in both halves. A feature is called reproducible only if its qualitative identity and quantitative support recur under a frozen correspondence rule.

Bootstrap resampling is used within each half for confidence intervals on density thresholds, mode locations, component mass, merge thresholds, and corridor bottlenecks. Bandwidth or neighbor-count sensitivity is reported over a narrow predeclared range around the selected primary value.

The complete analysis is repeated using at least one alternate official Big Five scoring representation if the SAPA release provides one. This is a measurement sensitivity test, not an opportunity to select the representation giving the most interesting result.

## What would count as a positive static-terrain result

A meaningful static terrain requires reproducible structure beyond an elliptical or Gaussian-copula population. Examples include multiple persistent high-density regions whose separation survives split-half replication, a stable low-density bottleneck between large regions, a reproducible high-support corridor connecting regions through a narrow part of the graph, or a persistent H1 feature stronger than the null expectation.

A single smooth unimodal cloud with no stable excess topology is also an informative result. The study is not designed to guarantee Swiss-cheese structure.

## What this study cannot establish

This study cannot show that dense regions are behavioral attractors, that sparse regions are unstable, that corridor density predicts ease of psychological change, that a low-density barrier resists transitions, or that any region is desirable or maladaptive. Those require longitudinal and outcome data.

Cross-sectional topology may generate a prospective transition hypothesis. Such a hypothesis becomes scientifically meaningful only if frozen before longitudinal testing and then evaluated against observed within-person trajectories.

## Model-side blinding rule

No model persona coordinates, model density maps, model clusters, model-family labels, or model terrain features may be used to define the human scoring system, density parameters, topology thresholds, mode definitions, corridor rules, or null models.

The complete human terrain, including scoring method, features, uncertainties, and frozen summaries, must be finalized before any human-to-model terrain comparison. This preserves the independence that makes a later correspondence result informative.

## Staged program

Stage 1 is the present static human terrain. Stage 2 compares the frozen human terrain with independently derived model terrain using coordinate-light properties such as neighborhood structure, connectivity, density rank, modes, bottlenecks, and topological persistence. Stage 3 tests whether frozen static-corridor predictions forecast actual longitudinal transitions. Stage 4 tests whether validated transition structure can support intervention or theory-of-change questions.

## Immediate execution sequence

First, recover and hash-verify the exact SAPA V5 source files against the existing project source manifest. Second, freeze the exact official Big Five key and scoring-direction table. Third, run the scoring-method validation without computing terrain. Fourth, commit the scoring decision and diagnostics. Fifth, compute the frozen static terrain and null comparisons. Sixth, freeze the human terrain before opening any model-side comparison.
