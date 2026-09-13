# AA-12 follow-up 2: cross-resolution human and model profile solution banks

Status: **COMPLETE INDEPENDENT INPUT BANKS; HUMAN/MODEL MATCHING NOT PERFORMED**

Date: 2026-09-13

Branch: `codex/aa12-cross-resolution-profile-banks`

Base: `4c7bf33b77412f8e1547a0817192fd50e9db7365`

Model-method freeze: `34dc9fa`

Numerical-bank freeze: `d0c902b`

Post-freeze semantic/figure commit: `423fde6`

## Result in brief

Two independent K=4–10 banks are now frozen for later Track 1 design. The human bank contains 49 aggregate SAPA latent profiles (34,104 profile-item rows) from the unchanged observed-cell six-category mixture. The model bank contains 49 activation-derived role clusters per model across Qwen 3 32B, LLaMA 3.3 70B, and Gemma 2 27B, using the same 275 designed roles and independently fitted spherical K-means solutions.

This phase does not select a human K, model K, common K, or human/model K pair. It calculates no human/model similarity or assignment. The evidence instead defines the within-domain resolution landscape and its warnings before a formal cross-domain matching and null-testing procedure is designed.

## Inputs and frozen methods

### Human

Source: Harvard Dataverse SAPA V5, DOI `10.7910/DVN/SD7SVE`, respondent artifact `sapaTempData696items08dec2013thru26jul2014.tab`; 23,679 respondents and all 696 canonical `q_*` behavioral items. The response codes are 1–6 and missing cells enter no likelihood term. RID, demographics, occupation, derived fields, and all respondent-level outputs are excluded.

The exact method frozen in `6b2e460f19efca5d4dbb47487461790651d34208` was reused: product-multinomial latent classes, alpha 0.5, identical respondent split, six fixed starts, identical seeds/convergence rules, two-percent size criterion, response-only anonymous ordering, and weighted square-root Jensen–Shannon/Hungarian alignment. All checked K=4–10 fit metrics reproduce the AA-12 numerical freeze `f0e55723eacc16730d4d9184bcb8bb9868458fb0` exactly.

### Models

Sources are the canonical released/local role tensors already used for established model geometry:

- Qwen/Qwen3-32B: `downloads/hf_vectors/qwen-3-32b/role_vectors/*.pt`, 275 × [64,5120], aggregate filename-plus-bytes SHA256 `3dc4bdcdcec301b3c947020f1c24755280af07aaf5fb8ab74ba10e3db9e73752`.
- LLaMA 3.3 70B: `downloads/hf_vectors/llama-3.3-70b/role_vectors/*.pt`, 275 × [80,8192], aggregate SHA256 `3b1863bf5b9770223c46c1b8a7b8e818b4b70c65d484eec78a07fcaa9f5aa235`.
- Gemma 2 27B: `downloads/hf_vectors/gemma-2-27b/role_vectors/*.pt`, 275 × [46,4608], aggregate SHA256 `5ec98556b81c8cf499f6c4521b6120196124aacebefcb55d33338e8d8ad12191`.

Each tensor is averaged over stored layers and L2-normalized. Each model/K is fit independently with exact spherical K-means: 100 fixed spherical-K-means++ starts, cosine objective, deterministic selection/labels, and 50 fixed 80% role-subsample refits with 20 starts each. The exact Gram implementation reproduces direct native-space cosine calculations and a full rerun reproduces all memberships, stability/continuity tables, centroid metadata, and centroid arrays exactly. The full specification is in `model/model_clustering_prefit_freeze.md`.

After the numerical freeze, the following already-saved 275×240 activation-cosine matrices were used descriptively only: Qwen `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`; LLaMA and Gemma `persona_trait_similarity_matrix.csv` files under `research/outputs/multimodel_trait_profile_pc_predictor/{llama,gemma}/`. They did not define or change clusters.

## Human K=4–10 bank

| K | Frozen status | Converged starts | Discovery MAP class sizes | Split-refit distance | Stability | Warnings |
|---:|---|---:|---|---:|---|---|
| 4 | eligible | 4/6 | 4,030; 4,689; 3,304; 2,183 | 0.091721 | moderate | response style |
| 5 | eligible | 5/6 | 3,405; 3,813; 2,847; 1,730; 2,411 | 0.111277 | moderate | response style |
| 6 | eligible | 4/6 | 2,967; 2,874; 2,479; 1,741; 2,507; 1,638 | 0.117515 | moderate | response style |
| 7 | eligible | 4/6 | 1,371; 2,794; 2,925; 2,001; 1,531; 1,364; 2,220 | 0.133243 | low | local optimum; response style |
| 8 | eligible | 4/6 | 1,266; 2,247; 2,489; 1,880; 1,945; 1,206; 1,237; 1,936 | 0.154578 | low | local optimum; response style |
| 9 | **DIAGNOSTIC / INELIGIBLE** | 3/6 | 1,172; 2,017; 1,523; 1,847; 1,218; 2,508; 1,422; 888; 1,611 | 0.158294 | low | convergence; local optimum; response style |
| 10 | eligible | 4/6 | 1,180; 1,203; 1,940; 1,890; 1,518; 2,001; 1,157; 777; 1,491; 1,049 | 0.153987 | low | local optimum; response style |

K=9 remains ineligible under the original rule and is published only for diagnostic browsing. This task creates no new preferred K; the prior K=4 BIC/ICL and K=10 predictive anchors remain unchanged.

### Human continuity and warnings

Aggregate expected-response profiles show recognizable nearest-profile continuity from each K to K+1, but continuity weakens at higher resolution. Mean nearest weighted square-root Jensen–Shannon distance is 0.035 for 4→5, 0.062 for 5→6, 0.038 for 6→7, 0.096 for 7→8, 0.084 for 8→9, and 0.115 for 9→10. Every lower-K profile has a mutual nearest higher-K profile through 8→9; only seven of nine do at 9→10. These are profile similarities, not respondent-level lineage, and all continuity involving K=9 inherits its diagnostic/ineligible status.

Independent respondent-split refits are moderate at K=4–6 and low at K=7–10. Administration-mask warnings remain absent at every K. Response-style warnings trigger at every K: replication balanced accuracy declines from 0.694 at K=4 to 0.401 at K=10 as chance falls from 0.25 to 0.10, while item-centered between-profile variance fractions remain 0.965–0.990. Thus generic response style materially predicts labels but does not fully remove item-pattern differences.

Post-freeze descriptions show recurring response configurations involving social ease/distress, reflective/imaginal engagement, task initiation/agency, attention seeking, rule breaking, and related item-level contrasts. These are anonymous descriptive themes, not Big Five classes, named constructs, natural types, or externally validated taxonomies. Full item evidence for every profile/K is in `human/human_semantic_browsing.md` and `human/human_semantic_items.csv`.

## Qwen K=4–10 bank

| K | Anonymous class sizes | Start median ARI | 80% refit median ARI | Stability (start/refit) | Size warning |
|---:|---|---:|---:|---|---|
| 4 | 33; 127; 50; 65 | 0.787 | 0.897 | moderate/moderate | no |
| 5 | 34; 91; 55; 65; 30 | 0.668 | 0.693 | low/low | no |
| 6 | 29; 42; 7; 53; 102; 42 | 0.757 | 0.876 | moderate/moderate | no |
| 7 | 8; 93; 28; 55; 45; 43; 3 | 0.724 | 0.796 | low/moderate | yes |
| 8 | 31; 48; 36; 2; 77; 3; 28; 50 | 0.633 | 0.643 | low/low | yes |
| 9 | 27; 88; 7; 26; 2; 1; 48; 48; 28 | 0.660 | 0.622 | low/low | yes |
| 10 | 35; 13; 42; 21; 30; 2; 3; 82; 10; 37 | 0.612 | 0.629 | low/low | yes |

Adjacent-K partition ARI is 0.608, 0.710, 0.862, 0.637, 0.811, and 0.773 from 4→5 through 9→10; NMI is 0.693, 0.732, 0.859, 0.702, 0.851, and 0.783. K=4 and K=6 are the comparatively robust resolutions under the frozen diagnostics; this is not a preferred-K decision. At K=4, post-freeze browsing describes anonymous clusters centered respectively on adversarial/irreverent roles, analytical/professional roles, grounded/social roles, and mythic/symbolic roles. Higher K partitions refine and sometimes isolate very small sets; the packet keeps every assignment visible without treating those sets as ontological types.

## LLaMA K=4–10 bank

| K | Anonymous class sizes | Start median ARI | 80% refit median ARI | Stability (start/refit) | Size warning |
|---:|---|---:|---:|---|---|
| 4 | 57; 152; 63; 3 | 0.821 | 0.882 | low/moderate | yes |
| 5 | 120; 47; 42; 63; 3 | 0.625 | 0.698 | low/low | yes |
| 6 | 40; 22; 28; 124; 58; 3 | 0.628 | 0.735 | low/low | yes |
| 7 | 53; 18; 118; 19; 19; 45; 3 | 0.672 | 0.737 | low/low | yes |
| 8 | 40; 17; 11; 50; 16; 121; 17; 3 | 0.658 | 0.691 | low/low | yes |
| 9 | 31; 39; 9; 7; 29; 5; 111; 41; 3 | 0.713 | 0.758 | low/moderate | yes |
| 10 | 26; 14; 9; 2; 49; 24; 1; 29; 115; 6 | 0.713 | 0.754 | low/moderate | yes |

Adjacent-K ARI is 0.630, 0.831, 0.769, 0.783, 0.713, and 0.787; NMI is 0.682, 0.772, 0.723, 0.704, 0.654, and 0.732. Every K contains a below-five-role cluster and start stability is low under the preregistered joint median/p10 rule. At K=4, post-freeze descriptions center on mythic/symbolic roles, analytical/teaching/professional roles, grounded/reactive social roles, and one tiny literal/primitive-role cluster. The full packet shows how larger partitions split these inventories while preserving the size/stability warning.

## Gemma K=4–10 bank

| K | Anonymous class sizes | Start median ARI | 80% refit median ARI | Stability (start/refit) | Size warning |
|---:|---|---:|---:|---|---|
| 4 | 68; 4; 67; 136 | 0.946 | 0.958 | moderate/moderate | yes |
| 5 | 4; 69; 53; 40; 109 | 0.624 | 0.842 | low/moderate | yes |
| 6 | 4; 59; 22; 29; 49; 112 | 0.673 | 0.772 | low/moderate | yes |
| 7 | 98; 4; 54; 26; 23; 21; 49 | 0.680 | 0.740 | low/low | yes |
| 8 | 10; 4; 32; 109; 17; 23; 35; 45 | 0.698 | 0.724 | low/low | yes |
| 9 | 3; 16; 41; 1; 106; 48; 22; 19; 19 | 0.709 | 0.729 | low/low | yes |
| 10 | 90; 40; 2; 1; 52; 13; 22; 26; 7; 22 | 0.624 | 0.675 | low/low | yes |

Adjacent-K ARI is 0.608, 0.854, 0.737, 0.639, 0.816, and 0.677; NMI is 0.657, 0.818, 0.725, 0.605, 0.764, and 0.692. Gemma K=4 has the strongest median start/refit agreement in its bank, but its four-role cluster triggers the frozen size warning and no K is selected. Its post-freeze K=4 packet describes mythic/symbolic, tiny literal/primitive, grounded/casual, and analytical/professional anonymous clusters; higher resolutions again add splits and singleton-scale warnings.

## Interpretation limits

The model role inventory is designed, not population sampled, so member proportions are not prevalence estimates and must not be compared with human class proportions. Spherical K-means returns a partition at every requested K; existence is not evidence that every resolution represents stable natural kinds. In particular, low start/refit stability and below-five-role clusters are visible rather than repaired away.

The human profiles remain subject to conditional-independence and response-style caveats. The model trait descriptions share activation-vector provenance with the role vectors. Semantic labels in the browsing prose are interpretations of already-frozen structures and did not alter numerical results.

## Scope boundaries and next step

No human/model matching was performed. No human/model cosine, correlation, nearest neighbor, Hungarian assignment, permutation test, correspondence score, or profile-coverage score was calculated. No same-K requirement was imposed, no preferred cross-domain K pair was chosen, and no cross-model cluster matching was performed.

No new inference, prompt generation, activation extraction, model API, GPU, or RunPod work occurred. No respondent-level output or individual imputation was created. External human-profile literature verification remains intentionally unperformed.

Track 1 remains ACTIVE. Tracks 2 and 3 remain PARKED. The next Track 1 task—only after user inspection—is to design and freeze the formal cross-resolution human/model pairing, comparability, and null-testing procedure.

## Artifact guide

- Human full bank: `human/human_cross_resolution_profiles.csv`
- Human K summary: `human/human_cross_resolution_solution_summary.csv`
- Human adjacent-K continuity: `human/human_adjacent_k_continuity.csv`
- Human semantic packet: `human/human_semantic_browsing.md`
- Human figures: `human/figures/`
- Model method freeze: `model/model_clustering_prefit_freeze.md`
- Per-model numerical membership: `model/{qwen,llama,gemma}/memberships.csv`
- Per-model named browsing membership: `model/{qwen,llama,gemma}/memberships_with_role_names.csv`
- Per-model summary and continuity: `model/{qwen,llama,gemma}/{solution_summary.csv,adjacent_k_continuity.csv}`
- Per-model trait summaries and browsing: `model/{qwen,llama,gemma}/{trait_profiles.csv,semantic_browsing.md}`
- Combined model trait bank: `model/model_cross_resolution_trait_profiles.csv`
- Verification: `verification_report.json`
- Complete inventory and hashes: `artifact_inventory.csv`
