# Human ↔ Model “Rosetta Stone” Profile Translation Study

Status: complete for the frozen aggregate Qwen primary analysis; no individual-level generalization.
Analysis commit: see Git history for the commit containing this report.

## Observed

The prior correspondence was recovered from local canonical AA-12 artifacts. It used the frozen 45-trait direct SAPA bridge, human K={4,5,6,7,8,10} aggregate profiles, four injectively matched model families, and a 20,000-draw search-adjusted trait-label permutation. Its focal K=10 result was back-transformed mean r=0.5201688 (p=0.00005), classified in its own preregistered artifact as strong aggregate correspondence. That result is descriptive input here, not an independent translation test.

This Rosetta follow-up froze a 12-trait anchor set with prior moderate-or-better human measurement support and evaluated the exact 33-trait complement. Qwen was primary; Llama/Gemma are fixed-pair descriptive replications. Matching used only the 12 anchors; target traits were excluded from matching.

Across 24 held-out matched-pair folds (four families × six eligible K values), identity/direct target-profile prediction averaged Pearson r=0.1500. Every learned candidate was worse on average: global intercept/scale r=-0.0102 (delta=-0.1602), trait-wise affine r=-0.1450 (delta=-0.2951), Procrustes r=-0.2362 (delta=-0.3863), and Ridge r=-0.2270 (delta=-0.3770). The best non-identity candidate was global intercept/scale, but its held-out improvement was negative.

The frozen structural nulls used 2,000 deterministic draws each. The best non-identity improvement statistic was −0.1602. Cluster-pairing, target trait-label, and joint-structure null p-values were 0.9305, 0.8996, and 1.0000, respectively. No null supports a positive translation improvement.

Trait residuals were heterogeneous rather than a compact recurring transform: for example, target residual signs were most consistent for anxious/bitter/calm/conscientious/patient/resilient/serene/stoic, but magnitudes varied substantially across matched pairs. See the residual CSV and consistency figure; these are descriptive, not fitted outcomes.

## Interpretation

The prior aggregate human/model profile correspondence is reproducible as a profile-shape correspondence under the recovered frozen inputs, but the present anchor-only held-out test does not show that recurring profile differences define a useful low-complexity Rosetta translation. The direct/identity target shape is the strongest tested baseline, and learned calibrations degrade out-of-sample target prediction.

Classification: **WEAK / ABSENT** for a supported aggregate Rosetta translation under this frozen design.

## Hypothesis

The weak individual V1 bridge may still reflect limitations of respondent-level measurement or literal trait matching, but this study provides no prospective evidence that a centroid-level affine, orthogonal, or regularized linear translation solves that problem.

## Unknown

Nothing here establishes whether an aggregate transformation could generalize to individual people, another human cohort, or another elicitation. The study does not explain V1 and was not optimized against V1 outcomes or errors. No human/model psychological equivalence, shared psychological ontology, or model personality claim follows.

## Reproducibility and privacy

Run `run_rosetta_translation.py` with the repository’s CPU environment. Seed is `2026091501`; all three null families use 2,000 draws. Only aggregate profiles, matched-pair summaries, and statistical outputs are committed. No respondent IDs, respondent rows, masks, posteriors, individual scores, or private V1 predictions are tracked.
