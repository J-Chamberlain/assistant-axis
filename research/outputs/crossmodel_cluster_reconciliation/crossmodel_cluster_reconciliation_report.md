# AA-12 Follow-up 3: Cross-Model Cluster Reconciliation and Consensus Profile Families

Date: 2026-09-13

Model used for analysis and synthesis: GPT-5.5

Status: **COMPLETE — MODEL ONLY; HUMAN COMPARISON NOT PERFORMED**

## Executive result

The independently frozen Qwen, LLaMA, and Gemma role partitions show strong, search-adjusted agreement over the same 275 roles. The best of all 343 resolution triples is Qwen K=6, LLaMA K=9, Gemma K=6, with mean pairwise AMI 0.644895. This is also the best triple after requiring every chosen partition's frozen 80% refit median ARI to be at least 0.70. A 5,000-draw null that preserves every model's exact partitions, cluster sizes, tiny groups, and within-model cross-K continuity gives `p=0.000200` for the searched maximum.

The optimum sits within an eight-triple near-best ridge rather than being the only supported resolution. A graph defined solely from direct shared-role overlap and neighboring-K persistence establishes a bounded candidate set of five components at the frozen Q6/L9/G6 anchor: four directly supported by all three model pairs and one two-model anchor component whose three-role core recurs in Qwen at neighboring K. The four broad three-model families are descriptively professional/analytical, mythic/symbolic, informal life-stage/social, and adversarial/competitive. A small primitive/literal developmental outlier family recurs across all three models but changes whether it is isolated or merged as K changes.

The most defensible representation is therefore hierarchical: four broad recurring families, a persistent developmental outlier/subdivision, and a near-consensus creative/conceptual region that the preregistered anti-transitivity rule declines to call a three-model family. This does not establish human personality types or human/model correspondence.

## Startup, continuity, and scope

The required master raw URLs were fetched in the specified order. All returned HTTP 200; visible canonical-file, state-role, last-updated, last-commit-when-present, latest-touch, and manifest-generation metadata agreed, followed by matching SHA-256 and byte counts. Canonical navigation, file index, raw URL index, research index, provenance registry, and findings ledger were consulted before locating inputs.

The prior cross-resolution branch was not integrated into canonical master, so this analysis branched directly from `1397cd670dc4eca5665a12d87d4b4179bab1e35a`. The method froze before any new cross-model result. Exact phase checkpoints are recorded in repository history.

Only model-side artifacts were loaded. No SAPA, NLSY97, human latent profile, human bridge, occupation, or human/model correspondence artifact entered the analysis.

## Frozen inputs

All inputs come from `research/outputs/cross_resolution_profile_banks/` at numerical-bank checkpoint `d0c902bdcd6cc0089f3f5cd353c19b6aeef29a97`.

| Model | Primary membership source | Frozen SHA-256 |
|---|---|---|
| Qwen 3 32B | `model/qwen/memberships.csv` | `2c4aee82f6ed7499401e45174b7e354bb4a4e09ff4600536c5534dc48a6a2f0d` |
| LLaMA 3.3 70B | `model/llama/memberships.csv` | `e4e74cd915c3490fd7e4adbddf8bb38e4058dc41e104acf7ab03a8a2285aa86f` |
| Gemma 2 27B | `model/gemma/memberships.csv` | `4df15ca4048a26a7b5ac3c93885baa1f9f0ffe866e2282c83d4c0520cf38d2d1` |

Each model contains exactly 275 identical opaque role IDs, one assignment per role at every K=4–10. Existing `solution_summary.csv` files supply frozen start/refit diagnostics. Existing `trait_profiles.csv` files supply post-match, within-model-standardized 240-trait summaries.

No partition was reclustered or retuned.

## Frozen method

The complete method is in `analysis_preregistration.md`.

- Primary partition metric: adjusted mutual information (AMI), arithmetic normalization.
- Secondary metrics: ARI, NMI, variation of information, and normalized VI.
- Search: all 49 K pairs for each of three model pairs and all 343 K triples.
- Near-best window: within 0.02 AMI of the relevant maximum.
- Quality sensitivity: frozen 80% subsample-refit median ARI at least 0.70; small clusters flagged, not excluded.
- Null: 5,000 deterministic draws, seed `2026091303`. Each model receives an independent role permutation used consistently across all of its K solutions.
- Cluster matching: direct shared-role intersection, Jaccard, overlap coefficient, directional containment, expected overlap, and hypergeometric enrichment with within-cell BH correction.
- Strong edge: `q<=0.01` plus the preregistered regular or tiny-cluster overlap threshold.
- Persistence: trace clusters by direct role overlap through the surrounding 3×3 K neighborhood; high at ≥0.75 support, moderate at ≥0.50, otherwise isolated.
- Consensus graph: only high/moderate persistent strong edges at the mechanically chosen anchor. Every represented model pair must have a direct edge, preventing unsupported transitive chaining.
- Trait confirmation: Pearson, Spearman, and centered cosine over the 240 frozen within-model-standardized trait profiles after membership edges froze.

## Pairwise cross-resolution agreement

All 147 K-pair comparisons are in `pairwise_k_agreement.csv`.

| Pair | Best K pair | AMI | ARI | NMI | Near-best K pairs | Search-adjusted p |
|---|---:|---:|---:|---:|---|---:|
| Qwen–LLaMA | 7 × 9 | 0.629692 | 0.648419 | 0.648935 | 7×9; 6×9; 6×10 | 0.000200 |
| Qwen–Gemma | 7 × 10 | 0.666955 | 0.688321 | 0.684714 | 7×10; 6×6; 6×10 | 0.000200 |
| LLaMA–Gemma | 4 × 4 | 0.674872 | 0.743895 | 0.680015 | 4×4 only | 0.000200 |

Under the frozen pairwise ridge definition, none of the three pairwise near-best sets is broad: Qwen–LLaMA and Qwen–Gemma each have three locally related high cells, while LLaMA–Gemma has one isolated pairwise maximum. The three-model result below nevertheless forms a broader ridge because neighboring combinations trade small amounts of agreement among the three constituent pairs.

## Three-model resolution search

The best triple is:

| Qwen K | LLaMA K | Gemma K | Qwen–LLaMA AMI | Qwen–Gemma AMI | LLaMA–Gemma AMI | Mean AMI |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | 9 | 6 | 0.618967 | 0.666448 | 0.649270 | **0.644895** |

Its mean frozen refit ARI is 0.802009: Qwen 0.875964, LLaMA 0.757782, Gemma 0.772280. It passes the ≥0.70 quality constraint and is also the quality-constrained maximum.

Eight triples lie within 0.02 of the maximum. They span Qwen K=6–7, LLaMA K=9–10, and Gemma K=6–7 or 10, satisfying the preregistered broad-ridge definition. Notable neighboring quality-passing triples include 7/9/6 (0.634794), 6/9/7 (0.632719), 7/9/7 (0.630955), and 6/10/6 (0.628670). Thus Q6/L9/G6 is a useful frozen anchor, not evidence for one universal model resolution.

The preserved-structure permutation maximum never reached the observed 0.644895 in 5,000 draws. With the preregistered plus-one correction, the search-adjusted p-value is `1/5001 = 0.00019996`. The same minimum p-value applies to each pairwise searched maximum.

## Cluster-level overlap and persistence

All 7,203 possible cluster pairs across the 147 model/K cells were evaluated. The frozen rule identifies 961 strong role-overlap edges:

- 688 high-persistence edges;
- 194 moderate-persistence edges;
- 79 isolated edges.

At Q6/L9/G6 there are 20 strong edges: 14 high, four moderate, and two isolated. The consensus graph uses the 18 high/moderate edges.

The dominant broad components show a mixture of one-to-one and split/merge structure:

- The analytical/professional (`MFamily_A`) and mythic/symbolic (`MFamily_B`) families are essentially one-to-one across the anchor solutions.
- Gemma `G06_D` combines structure divided across LLaMA `L09_A` and `L09_D`, with connected Qwen `Q06_F` and `Q06_C` profiles. This yields `MFamily_C` as a broad family with finer life-stage/social subdivisions.
- Gemma `G06_C` combines LLaMA `L09_C` and `L09_E` around Qwen `Q06_A`, yielding the split/merge adversarial `MFamily_D`.
- `Q06_B`, `L09_H`, and `G06_B` form a creative/conceptual near-consensus region, but the Qwen–LLaMA link has persistence 0.444 and is excluded. This is an intentional consequence of the frozen anti-transitivity rule, not an assertion that the region is absent.
- LLaMA `L09_F`—trickster, absurdist, aberration, bohemian, and jester—is unmatched at the anchor. Other models disperse these roles among broader groups.

## Tiny-cluster audit

Twenty-four model/K clusters contain fewer than five roles.

The clearest recurrent result is `{caveman, infant, toddler}`:

- LLaMA preserves the exact three-role cluster at every K=4–9.
- Qwen recovers the exact three-role cluster at K=7.
- Gemma retains the three roles plus `fool` at K=4–8.
- At K=9–10, Gemma and Qwen split out `caveman` and/or the `infant/toddler` pair; LLaMA does so at K=10.

This is a genuine three-model, cross-resolution outlier recurrence, although it is not a three-model component at the Q6/L9/G6 anchor. Its placement supports a hierarchical subdivision, not one universally isolated K-level type.

Qwen also isolates `{adolescent, procrastinator, teenager}` at K=8 and K=10. LLaMA and Gemma retain these roles together only within somewhat broader high-K profiles, making the exact tiny separation more Qwen-specific.

Singleton and two-role high-K refinements are documented rather than discarded. Their recurrence can be exact, but their size makes stability and trait magnitudes fragile.

## Candidate consensus families

The graph satisfies the frozen `ESTABLISHED_CANDIDATE_SET` rule: the searched agreement is significant, four accepted components directly span all three models, and the union of majority-role memberships covers 220/275 roles (80.0%) with zero majority-role ambiguity.

| Family | Anchor clusters | Models | Core roles | Majority roles | Mean Jaccard | Persistence | Descriptive theme |
|---|---|---:|---:|---:|---:|---:|---|
| MFamily_A | Q06_E; L09_G; G06_F | 3 | 100 | 107 | 0.895 | 1.000 | Analytical/professional/coordination |
| MFamily_B | Q06_D; L09_B; G06_E | 3 | 36 | 49 | 0.752 | 1.000 | Mythic/symbolic/numinous |
| MFamily_C | Q06_C; Q06_F; L09_A; L09_D; G06_D | 3 | 25 | 36 | 0.471 | 0.889 | Life-stage/social/adaptive |
| MFamily_D | Q06_A; L09_C; L09_E; G06_C | 3 | 20 | 25 | 0.452 | 0.694 | Adversarial/rebellious/competitive |
| MFamily_E | L09_I; G06_A | 2 at anchor | 0 across all 3 | 3 | 0.750 | 1.000 | Primitive/literal developmental outlier |

`MFamily_E` has three majority roles across its two anchor models; Qwen's exact recovery at K=7 is documented by the cross-resolution tiny audit rather than retrofitted into the anchor graph.

These are candidate model-side consensus families. They are not human-derived labels, model-role population prevalences, or ontological types.

## Secondary 240-trait confirmation

Trait-profile correlations support the broad role-overlap families:

| Family | Pairwise Pearson range | Pairwise Spearman range |
|---|---:|---:|
| MFamily_A | 0.854–0.925 | 0.854–0.914 |
| MFamily_B | 0.805–0.891 | 0.821–0.899 |
| MFamily_C | 0.834–0.893 | 0.826–0.885 |
| MFamily_D | 0.854–0.957 | 0.858–0.958 |
| MFamily_E | 0.831 | 0.841 |

Major recurring trait patterns are described in `semantic_consensus_summary.md`. Important model disagreements include generalist/avoidant for MFamily_A, existentialist/accessible for MFamily_B, inclusive/adaptable for MFamily_C, divergent/progressive for MFamily_D, and several extremely scaled brevity/intuition traits for tiny MFamily_E.

These correlations are not independent validation: role vectors and trait directions share activation provenance.

## Answers to the scientific questions

1. **Do the models repeatedly partition roles into recognizable broad families?** Yes. Direct shared-role evidence supports four broad all-model components plus a recurrent developmental outlier family.
2. **Which resolutions correspond most strongly?** The best and quality-constrained triple is Q6/L9/G6, but eight near-best triples form a ridge; no universal K is established.
3. **Is agreement stable across neighboring K?** Most strong edges are high or moderate in the neighboring-K audit (882/961), and the top triple lies on a ridge rather than standing alone.
4. **What happens to tiny clusters?** The caveman/infant/toddler group recurs unusually strongly across all three models; several finer singleton/two-role splits and Qwen's adolescent cluster are more resolution- or model-specific.
5. **Can a bounded model-side consensus set be supported?** Yes, as a candidate hierarchical representation: four broad three-model families, one recurrent outlier/subdivision, and a declined near-consensus creative region. It should not be flattened into a claim of one universal K.

## Reproducibility and artifacts

Primary machine-readable artifacts:

- `pairwise_k_agreement.csv`: every pairwise K cell and partition metric.
- `triple_k_agreement.csv`: all 343 triples and attached frozen quality diagnostics.
- `permutation_max_null.csv`: all 5,000 search-adjusted null maxima.
- `cluster_overlap_matrices.csv`: all 7,203 cluster-pair results.
- `cluster_overlap_edges.csv`: every frozen strong edge.
- `cross_resolution_persistence.csv`: neighboring-K persistence for every strong edge.
- `tiny_cluster_audit.csv`: full named tiny-cluster audit; the prior opaque-only checkpoint is retained.
- `cluster_trait_profile_similarity.csv`: secondary trait confirmation for every strong edge.
- `candidate_consensus_families.csv`, `consensus_family_roles.csv`, and `consensus_family_trait_profiles.csv`: consensus outputs.

Scripts:

- `run_partition_agreement.py`
- `run_cluster_correspondence.py`
- `run_trait_consensus.py`
- `build_semantic_outputs.py`

All figures are generated under `figures/`. Their selection and ordering rules are deterministic.

## Boundaries and unknowns

- No human data or SAPA profile was loaded.
- No model-to-human metric, correspondence, matching, projection, or K choice was performed.
- No model partition was reclustered.
- No new inference, prompts, activation extraction, external model API, GPU, or RunPod was used.
- Consensus families summarize a designed 275-role inventory, not population prevalence.
- Trait confirmation is secondary same-space evidence.
- It remains unknown whether these families correspond to human latent profiles, why the model recurrence exists, or whether it generalizes to additional model families and scales.

The next Track 1 task is to preregister the human/model profile correspondence and null-testing method over the already frozen geometry-blind bridge. That analysis has not begun.
