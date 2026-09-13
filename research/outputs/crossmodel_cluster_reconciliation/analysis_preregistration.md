# AA-12 Follow-up 3 Cross-Model Cluster Reconciliation: Frozen Method

Status: **PRE-ANALYSIS METHOD FREEZE**

Date frozen: 2026-09-13

Model used for analytical work: GPT-5.5

This record fixes the model-only reconciliation procedure before any new cross-model K-pair, K-triple, cluster-pair, tiny-cluster, or consensus-family result is calculated. It does not authorize human/model matching.

## Scope and frozen inputs

- Source checkpoint: `1397cd670dc4eca5665a12d87d4b4179bab1e35a`.
- Frozen numerical-bank checkpoint: `d0c902bdcd6cc0089f3f5cd353c19b6aeef29a97`.
- Models: Qwen 3 32B, LLaMA 3.3 70B, and Gemma 2 27B.
- K range: every integer from 4 through 10 for every model.
- Primary membership inputs: `research/outputs/cross_resolution_profile_banks/model/{qwen,llama,gemma}/memberships.csv`.
- Frozen quality inputs: each model's `solution_summary.csv` and `adjacent_k_continuity.csv`.
- Secondary trait inputs, opened only after membership correspondence is frozen: each model's `trait_profiles.csv`.
- Role names, semantic browsing packets, and trait labels are not used to calculate partition or membership correspondences. Opaque role IDs are the only primary comparison keys.
- All three membership banks must contain exactly the same 275 opaque role IDs, exactly once within each model/K solution. Any failure stops the analysis.
- No clustering, retuning, activation extraction, inference, prompt generation, API call, GPU, RunPod, human data, SAPA artifact, or human profile is permitted.

Input hashes are checked by the analysis script and recorded in its machine-readable summary. The frozen primary membership SHA-256 hashes are:

- Qwen: `2c4aee82f6ed7499401e45174b7e354bb4a4e09ff4600536c5534dc48a6a2f0d`
- LLaMA: `e4e74cd915c3490fd7e4adbddf8bb38e4058dc41e104acf7ab03a8a2285aa86f`
- Gemma: `4df15ca4048a26a7b5ac3c93885baa1f9f0ffe866e2282c83d4c0520cf38d2d1`

## Phase 1: exhaustive partition agreement

For each of Qwen–LLaMA, Qwen–Gemma, and LLaMA–Gemma, compare all 49 ordered K pairs with rows and columns K=4–10.

- Primary metric: adjusted mutual information (AMI), arithmetic-mean normalization as implemented by scikit-learn 1.8.0.
- Secondary metrics: adjusted Rand index (ARI), normalized mutual information (NMI; arithmetic normalization), variation of information in natural-log units, and normalized VI divided by `log(275)`.
- No composite metric will be created.
- Pairwise near-best set: every K pair with AMI within 0.02 of that model pair's maximum.
- A pairwise ridge is called broad when the near-best set contains at least four cells and spans at least two K values on both axes. Otherwise the maximum is described as isolated or locally limited.

## Phase 2: three-model resolution search and null

Evaluate all 343 triples `(K_Qwen, K_LLaMA, K_Gemma)`. The primary triple score is the unweighted mean of the three pairwise AMIs; all component AMIs remain visible.

- Triple near-best set: mean AMI within 0.02 of the global observed maximum.
- A broad triple ridge requires at least five near-best triples and variation across at least two K values in at least two models.
- Quality-constrained sensitivity includes a K only when its already-frozen median 80% role-subsample refit ARI is at least 0.70. Small clusters are flagged but not excluded.
- Consensus anchor triple: use the quality-constrained best triple if its mean AMI is within 0.02 of the global maximum; otherwise use the global maximum. Ties are broken by higher minimum pairwise AMI, higher mean frozen refit ARI, then lexicographically smaller `(K_Qwen,K_LLaMA,K_Gemma)`.

The search-adjusted null uses 5,000 deterministic permutations with seed `2026091303`.

For each draw, independently permute the 275 role indices for all three models, applying one model-specific permutation consistently to every K within that model. This preserves each exact partition, cluster-size vector, within-model cross-K continuity, and tiny-cluster structure while destroying cross-model role alignment. For every draw retain:

- the maximum AMI across each pair's 49 K comparisons; and
- the maximum mean pairwise AMI across all 343 K triples.

Monte Carlo p-values use `(1 + number(null >= observed)) / (5000 + 1)`. The maximum-statistic null, not a single-comparison null, governs claims about the searched optimum.

## Phase 3: cluster overlap and persistence

Compute every cluster-pair comparison within all 147 model-pair/K-pair cells. For each cluster pair report intersection, union, Jaccard, overlap coefficient, both directional conditional proportions, expected overlap from marginal sizes, and the upper-tail hypergeometric probability. Benjamini–Hochberg q-values are calculated separately within each model-pair/K-pair cell.

A cluster edge is **strong** when `q <= 0.01` and either:

1. intersection is at least 3 and (`Jaccard >= 0.30` or `overlap coefficient >= 0.65`); or
2. the smaller cluster has at most 4 roles, intersection is at least 2, and overlap coefficient is at least 2/3.

This rule allows one-to-one, split, merge, and small-cluster correspondences. No Hungarian one-to-one assignment is used as the primary result.

For every strong edge, examine the 3×3 neighborhood obtained by moving either K by at most one while remaining in 4–10. At each neighboring resolution, trace each original cluster to the cluster with greatest direct Jaccard overlap with its original role set; ties use overlap coefficient, intersection, then profile ID. Re-evaluate the frozen strong-edge rule for the traced pair.

- high persistence: at least four valid neighborhood cells and support fraction at least 0.75;
- moderate persistence: at least four valid cells and support fraction at least 0.50;
- isolated: otherwise.

Within-model parent descriptions use the already-frozen adjacent-K memberships and direct role overlap; semantic labels never determine lineage.

## Tiny clusters

Tiny means fewer than five roles, matching the earlier bank warning. Every tiny cluster at every K is retained. For each, record opaque members; its best overlap with every K in each other model; and its nearest broader lower-K parent, chosen by maximum fraction of tiny roles retained, then Jaccard, then the nearest lower K, then profile ID. Role names are joined only after numerical correspondence outputs are committed.

## Phase 4: secondary 240-trait confirmation

Trait confirmation occurs only after role-membership correspondence is committed. The input `within_model_standardized_score` is the frozen mean, within each cluster, of role-level trait values z-scored across the same 275 roles within model. For every numerically strong role-overlap edge, align the common 240 trait labels and report Pearson correlation, Spearman correlation, and cosine similarity after centering each 240-vector. Trait results cannot create, delete, or strengthen a membership edge and are explicitly same-activation-space secondary evidence.

## Candidate consensus families

Construct a tripartite graph using only clusters from the frozen consensus anchor triple. Include only strong edges with high or moderate resolution persistence. Connected components may contain more than one cluster from a model, permitting subdivisions.

To prevent unsupported transitive chaining, accept a component only if:

- it represents at least two models;
- every represented pair of models has at least one direct strong edge inside the component; and
- every such direct edge has at least moderate persistence.

Three-model components therefore require direct Qwen–LLaMA, Qwen–Gemma, and LLaMA–Gemma support rather than an A–B–C chain alone. Components are ordered by descending majority-role count, descending core-role count, then lexical node signature and assigned neutral IDs `MFamily_A`, `MFamily_B`, and so on.

For each family and role:

- core: assigned to the component by all three models;
- majority: assigned by at least two of three models;
- fringe: assigned by exactly one represented model.

Consensus status is `ESTABLISHED_CANDIDATE_SET` only if the search-adjusted global maximum has `p <= 0.05`, at least three accepted components represent all three models, and their union of majority roles covers at least 50% of the 275-role inventory. Otherwise status is `NOT ESTABLISHED`; two-model or partial components may still be reported diagnostically. Trait similarity is summarized afterward and does not gate the graph.

No universal K, flat taxonomy, population prevalence, human correspondence, causal mechanism, or natural psychological type is implied.

## Determinism and stopping

- Role order: lexicographically sorted opaque role ID.
- Model order: Qwen, LLaMA, Gemma.
- K order: 4 through 10.
- Model-pair order: Qwen–LLaMA, Qwen–Gemma, LLaMA–Gemma.
- Statistical ties use the explicit rules above, then lexicographic order.
- The analysis stops if inputs fail frozen hashes/inventory checks or if the specified metrics cannot be reproduced.
- Software: Python 3.12.12, NumPy 2.2.6, pandas 2.3.3, SciPy 1.17.0, scikit-learn 1.8.0, Matplotlib 3.10.8.

Semantic role names and trait labels may be inspected only after numerical partition and cluster correspondence checkpoints have been committed. Semantic interpretation cannot alter metrics, K choices, edges, persistence tiers, consensus graph, or family identifiers.
