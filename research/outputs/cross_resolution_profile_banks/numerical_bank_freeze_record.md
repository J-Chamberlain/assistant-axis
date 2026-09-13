# Cross-resolution numerical bank freeze

Status: **FROZEN BEFORE SEMANTIC BROWSING**

Date: 2026-09-13

The human K=4–10 aggregate profile bank and the Qwen/LLaMA/Gemma K=4–10 anonymous numerical partition banks have been materialized. This checkpoint precedes inspection of human item wording in the new cross-resolution bank, inspection of model cluster membership by role name, and use of trait labels to describe model clusters.

## Human numerical bank

The exact AA-12 method frozen in `6b2e460f19efca5d4dbb47487461790651d34208` was rerun without retuning. Every preregistered numerical metric checked at K=4–10 reproduced the prior frozen artifact exactly. K=4, 5, 6, 7, 8, and 10 retain their original eligible status; K=9 retains `DIAGNOSTIC / INELIGIBLE` status because only three of six starts converged monotonically. The bank includes all 49 anonymous profiles and all 696 item-category distributions per profile. Split-refit, missingness, and response-style diagnostics use the same frozen rules for every K.

No human respondent rows, RIDs, response masks, posterior memberships, MAP labels, inferred responses, or imputations were written.

## Model numerical banks

The method frozen in `model/model_clustering_prefit_freeze.md` was applied independently to each model. Every K=4–10 has a retained 100-start spherical K-means solution, 50 deterministic 80% role-subsample refits, start/refit stability metrics, opaque membership, adjacent-K overlap tables, and native centroid arrays and hashes.

The exact Gram calculations were checked against direct native-space cosine calculations. The first host execution exposed spurious NumPy/Accelerate floating-point-status warnings from finite matrix products; the authoritative runner uses explicit finite `einsum` contractions and single-thread backend settings. This changes no preprocessing, objective, seeds, fits, or selection rule. A complete independent rerun reproduced membership, start stability, subsample stability, adjacent-K continuity, centroid metadata, and every centroid array exactly; solution summaries were exact after excluding wall-clock runtime.

The model numerical runner emitted opaque IDs only (`R001`…`R275`). It did not read human data or trait matrices and did not emit semantic role names.

## Frozen boundary

This checkpoint fixes the human profiles, human eligibility labels, model memberships, model centroids, and within-domain K-to-K continuity evidence. Post-freeze code may join human item wording, model role names, and canonical model trait labels for descriptive browsing, but it may not refit, relabel by semantics, alter K, or change membership.

No human/model similarity, human/model match, cross-domain correspondence score, preferred K pair, same-K constraint, or cross-model cluster matching has been computed.
