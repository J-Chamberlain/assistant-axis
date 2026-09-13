# AA-12 follow-up pre-fit decision record

Status: **FROZEN BEFORE ANY SAPA CANDIDATE-CLASS FIT OR ITEM-WORDING INSPECTION**
Date: 2026-09-13
Thread: AA-12 follow-up
Track: Track 1 — independent profile-group correspondence (ACTIVE)
Model-selection labels: anonymous item IDs and `Profile A`, `Profile B`, … only

## Scope and source

The analysis will use the Harvard Dataverse SAPA V5 release, DOI `10.7910/DVN/SD7SVE`, respondent artifact `sapaTempData696items08dec2013thru26jul2014.tab`. Eligibility is the exact ordered set of 696 unique `q_*` behavioral item IDs in the canonical committed dictionary `research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv`, cross-checked against raw `ItemInfo696.csv` and the respondent-matrix header. RID will be read only to verify uniqueness and make a deterministic split, then discarded. All 22 other demographic, occupation, and derived non-item fields are excluded.

Expected integrity checks are 23,679 rows, 696 behavioral items, 719 total columns, unique RID, substantive response codes exactly 1–6, and empty behavioral-item fields as missing. Any mismatch stops the analysis. The one previously observed zero-answer row contributes a constant response likelihood and contains no class information; it will be excluded from parameter fitting and predictive-per-answer summaries but retained in total-row and posterior-certainty accounting with posterior equal to the fitted class prior. No other respondent-count threshold is applied.

No model geometry, model trait profile, model role, model cluster, model PC, external personality-profile solution, or published typology may be loaded. No external human-profile literature will be searched or inspected before or after the numerical freeze in this assignment.

## Primary model family

Primary model: a finite mixture of conditionally independent six-category item distributions (a product-multinomial latent-class model).

For respondent `i`, class `k`, observed item set `O_i`, class prior `pi_k`, and item-category probabilities `theta_kjr`, the observed-data likelihood is:

`P(x_i observed) = sum_k pi_k * product_{j in O_i} theta_{k,j,x_ij}`.

Missing cells create no response-likelihood term. They are neither filled nor treated as a seventh category. The ordered labels 1–6 are preserved in outputs, but the primary likelihood does not impose equal spacing or proportional-odds constraints. The model is fit by batch EM over a sparse respondent × item-category indicator matrix. M-step category counts receive a symmetric Dirichlet pseudocount of 0.5 solely to avoid zero probabilities. Class priors receive no added pseudocount.

The model’s conditional-independence assumption is recognized as strong for personality items. A fitted mixture is not automatically a set of psychological types.

## Candidate K and extension rule

Initial candidate range: every integer `K=2,…,12`.

The range extends sequentially through at most K=16 only if all of the following hold at the current upper boundary:

1. the boundary K is an eligible solution under the frozen convergence, class-size, and stability rules below;
2. it has the best validation mean log likelihood per actually answered item among fitted K values;
3. its paired improvement over K−1 exceeds both 0.0005 nats per answered item and one standard error of the respondent-level paired per-answer difference;
4. training AIC improves relative to K−1.

Extension stops at the first failed condition or K=16. K is never extended or selected because the profiles look meaningful or resemble any external/model grouping.

## Deterministic splits and seeds

Respondents with at least one observed item are assigned by a fixed RNG permutation with seed `2026091301`:

- discovery/training: first 60%;
- validation: next 20%;
- held-out replication: remaining 20%.

Rounding uses `floor(0.60N)` and `floor(0.20N)`; the remainder goes to replication. Missingness masks remain unchanged. Split assignments and RIDs are not committed.

Each K uses six fixed starts with seeds `2026091300 + 100*K + start_index`, start indices 1–6. Independent replication refits for the frozen candidate/preferred K use seeds `2026099900 + 100*K + start_index`, again six starts. Synthetic validation uses seed `2026091302`.

## Initialization and optimization

Each start initializes soft class responsibilities from `Dirichlet(0.35,…,0.35)`, then performs a smoothed M-step. EM settings:

- maximum iterations: 250;
- minimum iterations: 25;
- convergence tolerance: observed log-likelihood improvement below `1e-7` nats per observed response for five consecutive iterations;
- monotonicity tolerance: a decrease greater than `1e-8 * max(1, |LL|)` invalidates the start;
- probabilities clipped only for log evaluation at machine-safe `1e-300`;
- all computations use float64;
- no stochastic/minibatch EM.

A start is converged only when the consecutive-tolerance rule passes. For each K, the retained solution is the converged start with the highest discovery observed-data likelihood; exact likelihood ties choose the smaller seed. Report converged starts, best/worst/SD likelihood, iterations, and best-to-next likelihood spread. If fewer than four of six starts converge, K receives a convergence warning and is ineligible.

## Class size and anonymous labels

For K eligibility, both the smallest discovery posterior-effective class proportion and smallest discovery maximum-posterior (MAP) assigned proportion must be at least 0.02. This is a model-validity rule, not a final respondent inclusion threshold.

After fitting, classes are deterministically labeled by ascending unweighted mean expected raw response across the 696 items; exact ties use the lexicographic expected-score vector. Labels are `Profile A`, `Profile B`, and so on. This response-only ordering has no psychological meaning and cannot change K.

## Class alignment and stability

Formal class distance is the item-availability-weighted mean square-root Jensen–Shannon divergence across the 696 six-category item distributions. Discovery item counts define normalized item weights. Hungarian minimum-cost matching aligns classes.

Within-K start stability compares every converged start with the retained best solution. K is stable/eligible only if the median aligned class distance is at most 0.10. Distances above 0.05 or a best-to-second likelihood spread above 0.001 nats per observed response are flagged as meaningful local-optimum sensitivity even if K remains eligible.

Independent refit stability compares the retained discovery solution with the best six-start replication-only refit after Hungarian alignment. Mean aligned distance ≤0.075 is `high`, >0.075–0.125 `moderate`, and >0.125 `low`. Per-class distances and matched class proportions are reported. Replication stability is confirmatory and may downgrade the scientific conclusion but cannot trigger a semantic refit or post hoc K change.

## Fit statistics and model selection

For every K, report discovery observed-data log likelihood, free parameters `(K−1) + K*696*(6−1)`, AIC, respondent-N BIC, ICL (`BIC + 2 * discovery posterior entropy`), classification certainty (`1 − mean entropy/log(K)`), median maximum posterior, minimum effective/MAP class sizes, convergence/start spread, and validation plus locked replication log likelihood per observed response.

Validation predictive support uses the respondent-level `loglik_i / answered_i` values. Let K* have the highest eligible validation mean. A K is in the predictive one-standard-error set when its paired mean loss from K* is no larger than one standard error of that paired respondent-level difference. Information-criterion support is `delta BIC ≤10` or `delta ICL ≤10` among eligible K.

The defensible candidate set is the intersection of the predictive one-SE set and information-criterion-supported set. If nonempty, the preferred K is the smallest K in that set. If empty, no unique preferred K is claimed: retain the validation-best, BIC-best, and ICL-best eligible anchors as an explicitly conflicted bounded candidate set. A contiguous candidate range is reported only when the retained K values are contiguous. AIC, posterior certainty, class size, and stability remain reported evidence and can downgrade language; they do not override the frozen rule. No semantic information may enter selection.

## Posterior certainty

Posterior probabilities use only each respondent’s actually observed item responses under the frozen discovery profiles. Commit aggregate results only:

- median, mean, p10/p25/p75/p90 maximum posterior;
- shares with maximum posterior ≥0.50, ≥0.70, ≥0.80, and ≥0.90;
- raw and normalized posterior entropy;
- summaries by discovery/validation/replication/zero-answer status;
- certainty by deterministic deciles of answered-item count (duplicate quantile edges merged);
- Spearman correlation between answered-item count and maximum posterior;
- a fixed linear regression of maximum posterior on `log1p(answered count)`.

No minimum-answer threshold is selected. No respondent-level posterior, label, response mask, or completed profile is written.

## Missingness/administration diagnostics

Using frozen anonymous MAP labels only, report aggregate answered-item counts per profile and item observation frequency by profile. Train multinomial logistic regression on discovery rows to predict frozen profile label from (a) the 696-column binary response mask and (b) answered-item count alone; evaluate on validation and replication rows. Use L2 regularization, `C=1`, `lbfgs`, maximum 1,000 iterations, and class-balanced weights. Report accuracy, balanced accuracy, majority baseline, chance balanced accuracy `1/K`, adjusted accuracy above majority, and the maximum profile-wise item-observation-frequency range.

A strong mask warning is issued if replication balanced accuracy exceeds `1/K + 0.15` or adjusted accuracy exceeds 0.25. This diagnostic does not change class profiles.

## Response-style diagnostics

For each frozen profile, posterior-weight observed cells to estimate raw mean, variance, category-1 frequency, category-6 frequency, middle-category (3–4) frequency, extreme-category (1 or 6) frequency, high-category (5–6) frequency, low-category (1–2) frequency, high-minus-low tendency, and answered-item count. These are response-style descriptions, not keyed psychological constructs.

Separately, train the same class-balanced multinomial logistic model to predict frozen MAP label from answered-item count plus respondent-level raw mean, variance, category-1, category-6, middle, extreme, high, low, and high-minus-low summaries; evaluate on validation and replication. Report item-centered between-profile expected-score variance divided by total between-profile variance. A strong response-style warning is issued if replication balanced accuracy exceeds `1/K + 0.25` or the item-centered variance fraction is below 0.50.

Canonical reverse-key information may be inventoried after the numerical freeze but will not define or alter the primary classes. No named construct scores will be computed.

## Frozen profile outputs

For each retained numerical solution, save item ID, category probabilities 1–6, expected response, posterior-weighted item support, and approximate Dirichlet posterior standard errors. Save an anonymous profile × item expected-score matrix. Full machine-readable 696-item output is required.

Display items are the 60 items with largest max-minus-min frozen expected response across profiles, tie-broken by canonical item order. This response-derived display rule is frozen before semantic unblinding.

## Synthetic validation gate

Before any SAPA candidate fitting, simulate 4 known classes, 120 six-category items, and heterogeneous planned missingness with approximately 87% empty cells independent of class. Fit six starts at K=4. Hungarian-align estimated and true profiles using the frozen distance. The implementation passes only if:

- all probabilities normalize and observed likelihood is finite/monotone;
- mean aligned profile distance ≤0.075;
- adjusted Rand index ≥0.70 and aligned MAP accuracy ≥0.80;
- changing stored values underneath the missing mask changes neither likelihood nor posterior (`max absolute difference ≤1e-12`);
- an explicit label permutation is recovered exactly by Hungarian alignment;
- median posterior certainty in the top answered-count quartile exceeds the bottom quartile.

If this gate fails, do not fit SAPA until the implementation is corrected and the deviation is documented.

## Figures frozen in advance

Numerical/model-selection phase will produce:

1. `model_selection.png`: AIC/BIC/ICL and held-out per-answer likelihood by K;
2. `profile_heatmap.png`: expected responses on the fixed top-60 differentiating item IDs;
3. `profile_summary.png`: all 696 expected responses in canonical item order;
4. `certainty_vs_items_answered.png`: aggregate certainty bins only;
5. `class_sizes.png`: effective and MAP class sizes;
6. `missingness_diagnostic.png`: mask-only/count-only prediction versus baselines and item-frequency spread.

PCA, UMAP, and t-SNE will not be used.

## Semantic freeze and interpretation

The required sequence is binding:

1. commit this decision record and implementation settings;
2. pass synthetic validation;
3. fit/select using item IDs only;
4. save anonymous numerical profiles and diagnostics;
5. commit the numerical/profile freeze and record its SHA;
6. only then load item wording;
7. describe highest, lowest, and most differentiating items without changing K, refitting, or consulting external profile literature.

Interpretations remain restrained behavioral themes. The terms “universal human personality types” and model-derived labels are prohibited.

## Stopping, failures, and compute

CPU only. No RunPod or GPU. If sparse batch EM remains computationally prohibitive after profiling, stop and report the measured bottleneck rather than replacing the model with k-means, Gaussian mixtures, complete-case clustering, or imputed profiles. No semantically selected item subset is allowed.

Acceptable conclusions include a preferred K, a bounded neighboring set, no stable discrete structure, response-style-dominated classes, administration-mask-dominated classes, or another verified negative methodological result. No positive profile result will be forced.

## Privacy and prohibited outputs

Raw human data stay gitignored. Never commit RIDs, raw rows, masks, posteriors, MAP labels, inferred missing answers, individual completed profiles, or individual imputations. Only class-level probabilities, anonymous profile matrices, aggregate diagnostics, code, reports, and figures may be committed.

This phase performs no human/model comparison, no model inference, no activation extraction, no external model API call, and no external human-profile literature verification.
