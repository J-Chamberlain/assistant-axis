# Model cross-resolution clustering pre-fit freeze

Status: **FROZEN BEFORE NEW K=4–10 FITTING OR CLUSTER-MEMBERSHIP/ROLE-NAME INSPECTION**

Date: 2026-09-13

Thread: AA-12 follow-up 2

Scope: independent Qwen/LLaMA/Gemma model-side solution banks only

## Inputs and eligibility

The numerical inputs are the canonical released/local role tensors identified by repository navigation and provenance:

- Qwen/Qwen3-32B: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors/qwen-3-32b/role_vectors/*.pt`; 275 tensors of shape 64×5120; aggregate filename-plus-file-bytes SHA256 `3dc4bdcdcec301b3c947020f1c24755280af07aaf5fb8ab74ba10e3db9e73752`.
- Llama-3.3-70B: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors/llama-3.3-70b/role_vectors/*.pt`; 275 tensors of shape 80×8192; aggregate SHA256 `3b1863bf5b9770223c46c1b8a7b8e818b4b70c65d484eec78a07fcaa9f5aa235`.
- Gemma-2-27B: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors/gemma-2-27b/role_vectors/*.pt`; 275 tensors of shape 46×4608; aggregate SHA256 `5ec98556b81c8cf499f6c4521b6120196124aacebefcb55d33338e8d8ad12191`.

The aggregate digest is calculated over lexicographically sorted files by updating SHA256 with each UTF-8 filename and then its exact bytes. All three models must expose exactly the same 275 filename stems; any mismatch stops the run. Filenames are used mechanically for identity validation and later publication, not inspected semantically before the numerical freeze.

For each tensor, average over all stored layer rows in float64 and L2-normalize the resulting native-dimensional role vector. No PCA, feature standardization, trait vector, role instruction, human datum, SAPA profile, model PC, or prior cluster enters fitting. A zero or non-finite norm stops the run.

## Primary clustering model

Fit independent spherical K-means solutions for each model and each integer K=4,…,10. The objective is the sum, across roles, of cosine similarity to the assigned unit-normalized centroid. Each centroid is the unit-normalized arithmetic mean of its assigned unit role vectors. Computation may use the exact 275×275 cosine Gram matrix; this is mathematically equivalent to native-space assignment and centroid updating and avoids repeated high-dimensional multiplication.

Spherical K-means++ initializes the first center uniformly and subsequent centers with probability proportional to squared minimum cosine distance `max(1 − cosine, 0)^2`. Assignment ties choose the smallest internal cluster index. An empty cluster is deterministically repaired by moving the role with the smallest assigned-centroid similarity, breaking ties by the smallest opaque role index.

Stopping settings are maximum 300 iterations and either unchanged assignments or objective improvement below `1e-10 * max(1, abs(previous objective))` for five consecutive iterations. Objective decreases beyond `1e-10 * max(1, abs(previous objective))`, non-finite values, empty final clusters, or non-unit centroids invalidate a start.

## Starts, seeds, selection, labels, and size warning

Each model/K fit uses 100 fixed starts. For model index Qwen=0, LLaMA=1, Gemma=2, K, and one-based start s, the seed is:

`2_026_091 + 10_000*model_index + 100*K + s`.

The valid start with the largest objective is retained. Objective ties within `1e-12 * max(1, abs(objective))` choose the smaller seed. Report valid starts, best objective, objective per role, the converged-objective range/SD, iterations, and best-to-second gap.

Anonymous labels are assigned only after fitting. Clusters are ordered by the SHA256 of the sorted opaque member indices, with member count and internal cluster index as deterministic tie-breakers, then named `Q04_A`, `L04_A`, `G04_A`, and so forth. Labels carry no semantic meaning.

A solution with any cluster below five roles receives a `small_cluster_warning`; it is still retained in the browsing bank because this phase is not model-K selection. No preferred model K is selected.

## Start stability

Compare every valid start’s full 275-role partition with the retained partition using adjusted Rand index (ARI) and normalized mutual information (NMI). Report medians, minima, p10, and shares with ARI at least 0.90 and 0.75. Metrics are permutation-invariant; numeric cluster IDs are never compared literally.

Start stability labels are: `high` when median ARI ≥0.90 and p10 ARI ≥0.75; `moderate` when median ARI ≥0.75 and p10 ARI ≥0.50; otherwise `low`. This label is descriptive and does not choose K.

## Subsample-refit stability

Use 50 deterministic 80% role subsamples without replacement. For model index m and K, resample r uses seed `3_026_091 + 10_000*m + 100*K + r`. Fit each subsample with 20 spherical K-means++ starts whose seeds are `4_026_091 + 1_000_000*m + 10_000*K + 100*r + s`, s=1,…,20. Assign all 275 roles to the fitted subsample centroids using native-equivalent Gram similarities, then compare the full assignment with the retained full-data partition using ARI and NMI.

Report median, p10, minimum, and at-least-0.75 shares. Subsample stability labels use the same high/moderate/low thresholds as start stability. Failed resamples are reported; fewer than 45 valid resamples triggers a warning but no post hoc method change.

## Adjacent-K continuity

Within each model only, compare K with K+1 on the same 275 roles using ARI, NMI, and the full overlap table. Each higher-K cluster is linked descriptively to the lower-K cluster with maximum overlap; ties use higher Jaccard, then anonymous profile ID. Report overlap count, Jaccard, child share inherited from the parent, and parent share flowing to the child. This describes partition change and does not assert ontological nesting.

## Centroids and numerical outputs

Before semantic inspection, save opaque role membership, class counts/proportions, solution/start/subsample metrics, adjacent-K continuity, native-space unit centroid arrays, centroid hashes, source hashes, and software versions. Native centroids are reconstructed as normalized means of the frozen member role vectors. Machine-readable centroid arrays are NPZ files; metadata provide model, K, anonymous profile ID, dimension, norm, member count, and SHA256 of the float64 little-endian bytes.

The numerical freeze commit must occur before any role-membership browsing, trait-label inspection, semantic description, or human-bank semantic browsing in this phase.

## Post-freeze descriptions

After the numerical commit, role names may be joined to frozen opaque assignments. Nearest and furthest in-cluster roles use cosine similarity to the frozen native centroid. Existing canonical 275×240 same-model activation-cosine matrices may then summarize each frozen cluster; they may not change membership. Frozen sources are:

- Qwen matrix `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`, SHA256 `723d42415fe3a70221919fe8ae2aec2e2ebcdeae5bef89a1aeea55fdaccfe5d8`;
- LLaMA matrix `research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv`, SHA256 `74b2cb886967159fe4580b2dc8066cfe3ba789bedde7f0f380ee95240a3ed947`;
- Gemma matrix `research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv`, SHA256 `798c0618b9e468eec2e6d9083c96b2eef3d414f15f29d93180ff679614fea427`.

For each cluster/trait, report mean, median, population-standardized cluster mean across the 275 roles, and mean midrank percentile. Display traits are the 20 with largest absolute standardized cluster mean within model/K, tie-broken lexicographically. These are activation-derived descriptive summaries, not independent psychological measurements.

No human profile or item is loaded by the model numerical or semantic code. No human/model score, assignment, matching, or cross-domain K choice is computed. Cross-model profile matching is also outside scope.

## Compute and stopping rules

CPU only; no GPU, RunPod, model inference, activation extraction, prompt generation, or external model API. If the exact Gram implementation cannot reproduce direct native-space objective/assignments to `1e-10` on deterministic checks, or if any source identity/hash check fails, stop before fitting. Method changes require a new explicit freeze rather than silent substitution.
