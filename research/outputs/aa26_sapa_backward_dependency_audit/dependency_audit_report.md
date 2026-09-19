# Focused backward dependency audit

**Confirmed withdrawals are confined to AA-13's broad-score-dependent results and AA-12's historical/non-affect wellbeing surfaces.** No inspected AA-16–AA-25 scoring function imports AA-13's defective broad matrix or its missing reverse-keying implementation. AA-20, AA-22, AA-23, AA-24, and the AA-21 common-cohort sensitivity use one-item trait-proxy means; their own eligibility language is insufficiently explicit to establish a violation, so those results are **flagged for verification, not declared invalid**. AA-16, AA-17–AA-19, AA-21's primary fit, and AA-25 are unaffected by the defects examined here.

The authoritative concise table is [dependency_table.csv](dependency_table.csv): 20 result groups, with claim, exact dependency route, classification, reason, and required action. The four `WITHDRAWN_PENDING_REPAIR` rows override previous validity language for their specified claims and artifact slices. Original artifacts remain historical and unchanged.

| Result | Classification | Dependency / required action |
|---|---|---|
| Original pre-AA-10 snapshot | Potentially affected | Original script/folds absent; preserve as provenance-limited, not as verified original scoring. |
| AA-1 psychometric bridge | Unaffected | Explicit trait signs and official-key signed pairwise covariance. |
| AA-10 historical/non-affect measures | Unaffected | `score_items`, `domain_items`, and two-item eligibility; independently reconstructed. |
| AA-12 Big Five coordinates/support and content-balanced surfaces | Unaffected | Official keyed domains and explicit domain/content-count masks. |
| AA-12 historical-13 surface/fit | **Directly affected; withdrawn** | Unmasked `nanmean` feeds `isfinite` eligibility; repair minimum outcome count. |
| AA-12 non-affect surface/fit | **Directly affected; withdrawn** | Same count defect, plus vitality included contrary to the frozen AA-10 membership. |
| AA-13 broad structure/stability/alignment | **Directly affected; withdrawn** | Invalid broad means feed PCA, retention, alignment, and stability. |
| AA-13 prediction/comparison/negative conclusion | **Directly affected; withdrawn** | Invalid PC scores feed fits and common-cohort selection. |
| AA-13 raw provenance and separate frozen outcome/domain reconstruction | Unaffected | Hashes/counts are distinct from broad-score validity. |
| AA-16 association profile | Unaffected | `score_mean` explicitly orients and masks multi-item proxies below two observations. |
| AA-17 factor analysis | Unaffected | Saved model cosine matrices; human bridge is post-fit metadata. |
| AA-18 consensus/reconstruction | Unaffected | Model-profile targets, not SAPA broad targets. |
| AA-19 human structure | Unaffected | `basis`/`proxy` use signed pairwise item covariance, not respondent proxy means. |
| AA-20 outcomes and common-sample comparisons | Potentially affected | `trait_matrix` accepts one item; clarify per-proxy rule versus trait/pole/weight coverage. |
| AA-21 primary fit/transport | Unaffected | `bf_ok` independently requires correctly keyed Big Five and HiFWB scores with two items. |
| AA-21 common-cohort sensitivity | Potentially affected | `common` uses one-item proxy availability; primary path is separate. |
| AA-22 direct index/transport | Potentially affected | `score_traits` uses one item; freeze has no explicit per-proxy minimum. |
| AA-23 residual index/transport | Potentially affected | Same scorer; dependent weights/ranks inherit eligibility ambiguity. |
| AA-24 consensus transport/comparisons | Potentially affected | Imports AA-20 scoring; AA-23 ranks enter its comparison only. |
| AA-25 directions/probes | Unaffected | Selects AA-21 `full_overlap_primary` coefficients, not the flagged sensitivity. |

## Confirmed scope of withdrawal

**AA-13:** Withdraw substantive interpretation of the 79-scale broad profile, its PCs/loadings and retention counts, PC–Big Five/HiFWB associations, the reported three-dimensional subspace stability of 0.940, and broad-PC predictive comparisons. This includes the first-pass reported increment .015 and later mean bootstrap increment .0072 (interval [-.0071, .0223]), and the conclusion “no reliable incremental structure.” A negative conclusion is not protected from invalid measurement. The Big Five scorer itself is independently keyed, but its **AA-13 same-cohort benchmark** belongs to the withdrawn comparison because that cohort depends on invalid broad-PC eligibility. Do not replace the numbers or claim repaired effects.

The profile was originally a **predictor** of HiFWB in AA-13 and was considered as a possible reconstruction **target** in AA-26. It was not the human target of AA-18's model-profile reconstruction. Sharing vocabulary, an outcome freeze, an eligibility reference count, or a random seed does not make the broad-score defect propagate.

**AA-12 historical-13:** The published conditional metrics use N=6,549. An availability-only check of the same hash-matched source reproduces that cohort using one observed outcome item, whereas the documented two-item rule yields N=3,972. Thus 2,577 one-item outcome rows entered the saved cohort. Withdraw that outcome's means, aggregate surface cells, fitted coefficients, conditional slices, and derived interpretations—not the entire multi-outcome bundle.

**AA-12 non-affect:** The saved cohort is N=5,715. Enforcing two observations on its own nine-item set gives N=3,003: 2,712 one-item rows were included. It also includes `q_832` (Vitality), whereas AA-10's frozen non-affect score removes it. Applying AA-10's eight-item membership and two-item rule gives N=2,548. These two differences must not be conflated. Withdraw the claim of frozen-AA-10 reproduction and its non-affect outcome slices pending both definition and eligibility repair.

Mixed AA-12 files requiring outcome-specific status overrides are `conditional_model_metrics.csv`, `conditional_model_bundle.json`, `wellbeing_surface_aggregate.csv`, and `wellbeing_surface_bundle.json`, plus displays generated from their `historical_13` and `non_affect` entries. No viewer was changed. The default content-balanced >=2 surface remains separate; its saved N=3,257 matches AA-10, and its group-count mask is enforced. Big Five terrain/support N=8,585 is also unaffected.

## Why later one-item proxies are flagged rather than withdrawn

AA-16 explicitly requires two items for a multi-item proxy. AA-19 instead models signed **pairwise item covariance** and never freezes a respondent proxy mean. AA-20 subsequently defines observed proxy traits, pole coverage, and absolute-weight coverage; it explicitly requires two **outcome/domain items**, but does not explicitly require two items **per proxy**. Its code counts a proxy observed at one item. AA-22 repeats that construction; AA-23 and AA-24 inherit related scoring with shorter documentation. This is a change from AA-16, but an automatic declaration that their own rule was violated would exceed the evidence.

Their explicit reverse-keying and two-item HiFWB/Big Five masks pass source and synthetic checks. The unresolved issue is the measurement/eligibility definition and any claimed continuity with AA-16. Required next action is a narrow rule/provenance clarification, followed only if needed by a targeted minimum-item sensitivity—not a blanket rerun. Dependent human weights and transported rankings inherit this flag; unaffected AA-18 axes and AA-21 primary coefficients do not.

## Correction to the preceding AA-26 feasibility audit

The `q_55` source-membership difference is real, but it is **not an undocumented mapping problem**. The earlier psychometric scorer's `build_source_scale_map` explicitly maps `IPIP100:B5:E` to the official 19-item `IPIP100extra` key and records the 19-of-20 overlap. AA-10's specification also explicitly records the anomaly. The preceding audit's suggestion that this mapping was missing was too strong. Existing artifacts provide the mapping needed for a future corrected version; no new item or inferred sign is necessary. This correction does not validate AA-13's unkeyed means or its unmasked one-item cells. No broad target has been rebuilt here.

## Evidence and limits

Sources are pinned to AA-26 parent `bcec11d9db9b2e87554012bb3d2f5f2a8201df6f`, AA-13 `045ac766949356ffb31705c69ba677824faf65b8`, and AA-10 `f4cc10bd3392c4432eccfa8244a3e58b5eef31a5`. `source_inventory.csv` records hashes, commits, and full paths; `scoring_function_locations.csv` provides exact function line locations. Static review followed scoring through masks, matrix construction, model inputs, and transports, rather than treating mentions as computational dependencies.

Verification used extracted scoring functions on tiny synthetic arrays and one raw-data **availability-only** pass. No historical analysis program was imported or run; no model was fitted, no respondent scores exported, no model inference performed, and no target repaired. The 35 checks and aggregate cohort counts are in `verification_report.json` and `eligibility_verification.json`. “Unaffected” means unaffected by the three specified scoring/target defects, not a general replication or endorsement of all analytical choices. Deferred AA-13 analyses are not described as withdrawn numerical results because they were never run. The original pre-AA-10 script/folds remain unavailable, so that snapshot cannot receive an implementation-level clearance.

Canonical claims/state/provenance/navigation records carry these withdrawals and flags. **Stop point: backward audit complete; target reconstruction remains unstarted.**
