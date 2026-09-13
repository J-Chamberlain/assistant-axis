# AA-12 follow-up numerical/profile freeze record

Status: **FROZEN BEFORE ITEM-WORDING UNBLINDING**

The semantically blinded analysis evaluated K=2 through K=12 using only canonical item IDs and observed response categories. K=12 failed the frozen eligibility rule because only three of six starts converged and its median start-profile distance exceeded 0.10, so the mechanical extension rule prohibited fitting K=13–16.

The frozen criteria do not yield a unique K. Validation predictive likelihood favors eligible K=10, while both BIC and ICL favor K=4. Their one-standard-error and information-criterion support sets do not intersect, so the preregistered fallback freezes K=4 and K=10 as conflicted anchors. K=10 is the reference solution for the already-frozen aggregate certainty and artifact diagnostics because it is the validation-best eligible solution; this designation is not a claim that K=10 is a unique winner.

Independent replication refitting rates K=4 stability as moderate (mean aligned distance 0.091721) and K=10 stability as low (0.153987). Consequently, a stable fine-grained ten-profile structure is not established. K=4 is more reproducible but remains only one statistically supported anchor, not an ontological type count.

All class labels are anonymous and deterministic. Full class-category item distributions and expected-response matrices for both anchors are frozen in `frozen_profile_item_probabilities.csv` and `frozen_profile_expected_scores.csv`. The required item-wording unblinding may begin only after the commit containing this record and those matrices. Semantic interpretation cannot change K, refit any solution, or alter these numerical profiles.

No respondent-level data, response masks, split assignments, posterior probabilities, MAP labels, or imputed responses are included. No model-side artifact or external human-profile literature was loaded.
