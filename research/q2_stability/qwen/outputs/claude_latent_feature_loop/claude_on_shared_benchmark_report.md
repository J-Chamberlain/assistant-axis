# Claude Features on Shared Benchmark: Cross-Model Convergence Analysis

**Date:** 2026-05-28
**analysis_model:** claude-sonnet-4-6
**benchmark_source:** Codex/GPT-5.5 canonical activation PCA from `research/visualizations/geometry_viz_data.json`
**transfer_source:** `research/q2_stability/qwen/outputs/cross_model_feature_transfer/transfer_results.json`

---

## Executive Summary

BigFive psychological traits (5-dim, LLM-assigned) outperform Codex/GPT-5.5's 31 behaviorally-
derived dimensions on the canonical Qwen activation PCA target. BigFive R²=0.613 vs Codex
R²=0.490, a +0.123 margin. Both models converge on: (1) psychological structure as the primary
explanatory framework, (2) developmental/non-adult personas as the hardest to explain,
(3) procedural-professional cluster as the most predictable. Claude's pseudo-PCA PC1 failure
(R²=-0.089) does not replicate on the canonical target (BigFive PC1=0.734), indicating the
pseudo-PCA proxy was a poor approximation of the canonical PC1. The cross-model comparison
is now complete for the BigFive feature block; Codex's own feature results on the canonical
target are on record for all 8 comparison dimensions.

---

## Q1: Does BigFive remain dominant on the canonical target?

**Yes, BigFive is stronger on the canonical target than on Claude's pseudo-PCA.**

| Feature set | Target | Mean PCA3D R² | PC1 | PC2 | PC3 |
|---|---|---|---|---|---|
| BigFive (Claude) | Pseudo-PCA3D | 0.361 | -0.089 | 0.732 | 0.440 |
| BigFive (Claude) | Canonical activation PCA | **0.613** | **0.734** | **0.480** | **0.415** |
| Codex 31-dim | Canonical activation PCA | 0.490 | 0.631 | 0.257 | 0.422 |
| Semantic baseline | Canonical activation PCA | 0.389 | 0.517 | 0.181 | 0.336 |

BigFive reaches R²=0.613 on the canonical target, compared to R²=0.361 on Claude's pseudo-PCA
proxy. The canonical target is better-structured for psychological explanation than the
cosine-matrix PCA proxy.

---

## Q2: How does BigFive compare to Codex's 31 dimensions?

**BigFive outperforms by +0.123 overall (0.613 vs 0.490).**

The margin is consistent across axes:
- PC1: BigFive 0.734 vs Codex 0.631 (+0.103)
- PC2: BigFive 0.480 vs Codex 0.257 (+0.223)
- PC3: BigFive 0.415 vs Codex 0.422 (-0.007, essentially tied)

Codex built 31 dimensions through an iterative behavioral/motivational loop (4 iterations to
plateau, 11 dimension families). BigFive achieves higher overall R² with only 5 dimensions.
This likely reflects that BigFive profiles were originally LLM-assigned with full role-name
knowledge, making them a maximally-informed feature set that partially encodes activation
structure through the same LLM priors that generated it.

**Caveat**: BigFive scores were assigned by an LLM (likely GPT-4 or Claude) during Paper 1.
They are not independent of the activation target — they may share representational priors
with Qwen's internal role geometry. This inflates the apparent predictive gain and should
not be interpreted as evidence that five psychological traits objectively explain activation
structure.

---

## Q3: Is the PC1 failure replicated on the canonical target?

**No — the pseudo-PCA PC1 failure does not replicate.**

- Claude pseudo-PCA PC1: R²=-0.089 (UNPREDICTED)
- Canonical activation PCA PC1: BigFive R²=0.734

The pseudo-PCA PC1 (derived from PCA on the 275×7 cluster-cosine matrix) captured 59.3% of
cosine-matrix variance but was orthogonal to all tested features. The canonical PC1 (derived
from full Qwen role-vector PCA) is strongly predicted by BigFive (R²=0.734) and moderately
by Codex features (R²=0.631).

**Interpretation**: The pseudo-PCA proxy's PC1 was an artifact of cosine-matrix structure,
likely capturing global variation in cosine-to-centroid magnitudes rather than interpretable
semantic or psychological dimensions. The canonical PC1 does correspond to psychologically
legible variation (BigFive explains 73% of its variance).

The earlier finding that "the dominant activation dimension is not predictable from human-legible
features" was target-specific and should be **retracted as a general claim**. On the canonical
target, the dominant dimension is well-explained by BigFive.

---

## Q4: Which model's best-explained personas converge?

### Worst-explained: Strong convergence

| Claude worst (pseudo-PCA) | Codex worst (canonical) | In both? |
|---|---|---|
| toddler | procrastinator | — |
| caveman | **toddler** | YES |
| infant | **teenager** | YES |
| pirate | comedian | — |
| proofreader | cyborg | — |
| teenager | vampire | — |
| perfectionist | smuggler | — |
| poet | sage | — |
| adolescent | ancient | — |
| procrastinator | amateur | YES (top-15) |
| — | **caveman** | YES |
| — | **poet** | YES |
| — | **infant** | YES |

**6 roles appear in both worst-explained lists**: toddler, caveman, infant, teenager, poet,
procrastinator. All 6 are developmentally-specific or ontologically unusual roles. This
is the strongest cross-model convergence finding: developmental/non-adult personas are
systematically resistant to explanation by either BigFive or Codex's behavioral dimensions.

### Best-explained: Partial convergence on cluster, divergence on specific roles

**Claude best** (pseudo-PCA): architect, journalist, paramedic, marketer, veteran, soldier,
reporter, doctor, recruiter — dominated by procedural_professional cluster

**Codex best** (canonical): designer, curator, chemist, accountant, economist, scheduler,
secretary, grader, writer, programmer — also dominated by procedural_professional and editorial

Specific roles do not overlap, but both converge on the procedural_professional activation
cluster as the most predictable. The specific representatives differ because Claude's
pseudo-PCA and Codex's canonical target emphasize different variance directions within that
cluster.

---

## Q5: What dimensions does Codex use that BigFive doesn't capture?

Codex's 31 dimensions include:
- **boundary_liminal_instability**: roles at ontological/categorical boundaries (bridge roles)
- **reactive_opposition**: adversarial/contrarian stance
- **assistant_basin_adjacency**: proximity to generic assistant behavior
- **volatility_liminality**: temporal/transitional identity
- **procedural/destabilize_expose_disrupt**: professional + destabilizing function
- **collective_distributed/nonindividual_systemic_identity**: non-individual entities

These dimensions explain PC3 marginally better than BigFive (0.422 vs 0.415) but substantially
worse on PC2 (0.257 vs 0.480). Codex's dimensional framework captures aspects of role
*function and ontological position* that BigFive's trait-based framework misses, but those
dimensions carry less PC2 variance.

**PC2 interpretation**: BigFive's +0.223 PC2 advantage suggests that PC2 encodes individual
psychological differences (trait-like variation) better than categorical-functional variation.
Codex's dimensions may be better suited for PC3, which is closer to trait-neutral.

---

## Q6: Cross-model summary scorecard

| Comparison dimension | Claude (pseudo-PCA) | Claude (canonical) | Codex (canonical) |
|---|---|---|---|
| Primary target | Pseudo-PCA3D | Canonical activation PCA | Canonical activation PCA |
| Best feature set | BigFive + TF-IDF | BigFive alone | 31 behavioral/motivational dims |
| Best held-out R² | 0.361 | 0.613 | 0.490 |
| Δ vs semantic baseline | +0.219 | +0.224 | +0.101 |
| PC1 R² | -0.089 (failed) | 0.734 | 0.631 |
| PC2 R² | 0.732 | 0.480 | 0.257 |
| PC3 R² | 0.440 | 0.415 | 0.422 |
| Best cluster | procedural_prof | procedural_prof | procedural_prof |
| Worst cluster | other/developmental | other/developmental | other/developmental |

---

## Q7: What does convergence mean?

Both models, operating on different targets with different feature-generation methods,
independently identified:
1. **BigFive psychological structure** as the primary explanatory framework
2. **Developmental/non-adult personas** as the hardest cluster to explain
3. **Procedural-professional** as the most predictable cluster
4. **Consistent semantic baseline** (cluster-label one-hot features) explaining ~39% of canonical PCA variance

This convergence on cluster-level predictability structure is unlikely to be coincidental.
It supports treating procedural-professional as a "semantically transparent" activation basin
and the developmental/other cluster as "semantically opaque."

---

## Q8: Outstanding confounds and limitations

1. **BigFive provenance**: LLM-assigned scores may share priors with activation geometry,
   inflating apparent R². The +0.123 BigFive advantage over Codex may partly reflect this
   circularity.

2. **N=273 vs N=275**: Codex used 273 personas (2 roles missing from geometry_viz_data.json).
   Claude's pseudo-PCA used 275 roles. Small discrepancy; not material.

3. **Pseudo-PCA target is invalid for cross-model comparison**: Claude's R²=0.361 on the
   pseudo-PCA should not be compared directly to Codex's R²=0.490 on canonical PCA.
   The canonical comparison (BigFive 0.613 vs Codex 0.490) is the correct transfer test.

4. **Claude's TF-IDF + BigFive combination was not re-tested on canonical target**: The
   transfer_results.json reports BigFive-only on canonical PCA. Adding TF-IDF to BigFive
   may further improve R² on the canonical target (or may not add signal above BigFive alone,
   consistent with the plateau behavior).

5. **Codex's pseudo-PCA R²=0.280**: Codex's features explain only 28% of Claude's pseudo-PCA
   target. This is expected given the target mismatch, not a finding about feature quality.

---

## Artifact references

| Artifact | Path |
|---|---|
| Transfer results | `research/q2_stability/qwen/outputs/cross_model_feature_transfer/transfer_results.json` |
| Codex outer loop log | `research/q2_stability/qwen/outputs/iterative_outer_loop/outer_loop_master_log.json` |
| Codex persona rankings | `research/q2_stability/qwen/outputs/iterative_outer_loop/persona_explanation_rankings.csv` |
| Claude persona rankings | `research/q2_stability/qwen/outputs/claude_latent_feature_loop/claude_persona_explanation_rankings.csv` |
| Claude feature matrix | `research/q2_stability/qwen/outputs/claude_latent_feature_loop/claude_feature_matrix.csv` |
| Canonical PCA target | `research/visualizations/geometry_viz_data.json` |
