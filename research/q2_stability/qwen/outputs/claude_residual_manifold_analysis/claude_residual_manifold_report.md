# Claude Residual Manifold Analysis Report

**Date:** 2026-05-28
**Analysis model:** claude-sonnet-4-6
**Target:** Canonical Qwen activation PCA3D (N=273 personas)
**Baseline:** semantic one-hots (k=7) + BigFive, R²=0.613

---

## Executive Summary

After BigFive explains the broad psychological structure of Qwen activation geometry (R²=0.613), two complementary residual features substantially increase predictive power: (1) cosine similarity to reference persona centroids (5 clusters of high-residual personas), and (2) TF-IDF SVD15 coordinates from the no-label prompt corpus. SVD15 alone reaches R²=0.707 (+0.094), 5/5 splits passing the criterion. Combined, R²=0.707 (+0.094), 4/5 splits. The first approach tested (abstract TF-IDF reference documents) failed entirely, with both bundles discarded at plateau after 2 iterations. The residual manifold is best described as a multi-polar structure combining developmental/pre-adult identity, collective/nonindividual agency, symbolic/archetypal cultural roles, and boundary-transgressive liminal roles — none of which are captured by the five-dimensional BigFive trait space.

---

## 1. Interpretation Target: What structure remains after BigFive?

### Worst-explained personas under BigFive alone (activation residual ranked)

| Rank | Persona | Cluster | BigFive residual |
|------|---------|---------|-----------------|
| 1 | procrastinator | other | 68.0 |
| 2 | toddler | other | 59.8 |
| 3 | teenager | other | 53.1 |
| 4 | smuggler | grounded_social | 51.0 |
| 5 | hoarder | other | ~47 |
| 6 | infant | other | ~44 |
| 7 | adolescent | other | ~43 |
| 8 | daredevil | combative_iconoclast | ~40 |
| 9 | loner | grounded_social | ~38 |
| 10 | exile | grounded_social | ~36 |

Three structural groups are visible:
- **Developmental/pre-adult**: toddler, infant, teenager, adolescent, caveman — no coherent adult trait profile
- **Low-agency stalling**: procrastinator, hoarder — passive modes not well-captured by conscientiousness alone
- **Liminal/boundary-transgressive**: smuggler, daredevil, loner, exile — roles defined by outside-of-normal-structure position

### PC2 as the primary axis for residual features

Under BigFive alone, PC1=0.734, PC2=0.480, PC3=0.416. After adding SVD15, PC1=0.819, **PC2=0.585**, PC3=0.528. The +0.105 gain on PC2 is the largest per-axis improvement. This confirms that PC2 encodes social/relational/identity structure — the dimension most distorted by developmental and liminal roles.

---

## 2. Approach 1 Failure: Abstract TF-IDF Reference Documents

**Design:** 8 abstract reference documents (developmental_prematurity, low_agency_stalling, collective_nonindividual, prereflective_sensation, symbolic_archetypal, parasitic_dependency, liminal_transgressive, unstable_identity). Compute cosine similarity of each persona to each reference document.

**Result:** Both test bundles discarded; plateau after 2 iterations; final R²=0.613 (zero improvement).

**Diagnostic:** Mean cosine similarities ranged from 0.010 to 0.022 — extremely low, indicating near-zero vocabulary overlap between abstract concept text and persona prompt text. The residual cluster was only 1.40× more coherent than random in TF-IDF space. Personas in the "developmental" residual region do not use abstract developmental-psychology vocabulary; their prompts use concrete behavioral and situational language that the reference documents don't capture.

---

## 3. Approach 2 Success: Reference Persona Centroids

**Design:** For each residual cluster, compute mean TF-IDF vector of 4–5 representative personas. Each centroid feature = cosine similarity of a persona to that cluster centroid. Five centroids: developmental, stalling, collective, symbolic, liminal.

**Result: R²=0.643 (Δ=+0.030), 4/5 splits pass — PASSES criterion.**

### Why centroids succeed where reference docs fail

Reference persona centroids are grounded in actual persona prompt language rather than human-generated abstract vocabulary. When we ask "how similar is this persona to the average of toddler + infant + teenager + adolescent + caveman?", we're measuring proximity in the actual text space that shaped the activations, not proximity to an external vocabulary.

### Centroid statistics

| Centroid | Mean sim | Max sim | Top scorers |
|----------|----------|---------|-------------|
| sim_to_developmental | 0.062 | 0.641 | adolescent(0.641), teenager(0.610), infant(0.539), caveman(0.478), toddler(0.475) |
| sim_to_stalling | 0.055 | 0.563 | amateur(0.563), student(0.553), procrastinator(0.515), hoarder(0.514) |
| sim_to_collective | 0.050 | 0.650 | swarm(0.650), hive(0.648), egregore(0.527), parasite(0.475) |
| sim_to_symbolic | 0.061 | 0.543 | bard(0.543), fool(0.540), sage(0.530), pirate(0.523) |
| sim_to_liminal | 0.056 | 0.551 | daredevil(0.551), loner(0.517), exile(0.515), smuggler(0.503) |

Key observation: **centroid self-similarity is high and near-neighbor falloff is sharp** — each centroid cleanly captures its target cluster. The second-highest scorers (mycorrhizal, hermit, guru, competitor) are semantically adjacent but not identical, confirming that the features capture meaningful neighborhoods rather than just cluster membership.

---

## 4. Approach 2b: TF-IDF SVD15

**Design:** TruncatedSVD(n=15) of the full no-label prompt TF-IDF matrix (SVD explained variance: 13.8%).

**Result: R²=0.707 (Δ=+0.094), 5/5 splits pass — best single model.**

SVD15 outperforms the interpretable centroid features by a substantial margin (+0.064 R²) and achieves 5/5 split passes compared to 4/5. This indicates that continuous prompt-space variation beyond the 5 named centroids carries substantial additional signal. The SVD components are not individually interpretable, but their aggregate prediction quality confirms that the no-label prompt corpus contains latent structure that BigFive's 5 dimensions do not capture.

**Combined model (centroids + SVD15): R²=0.707 (Δ=+0.094), 4/5 splits.**

The marginal gain of adding centroids to SVD15 is near-zero (+0.000), indicating that the centroid features are largely redundant with SVD components — as expected, since the centroids are also derived from the same TF-IDF space.

---

## 5. Residual Structure After Best Model

### Still-hard personas in combined model

| Rank | Persona | Cluster | Combined residual |
|------|---------|---------|-----------------|
| 1 | daredevil | combative_iconoclast | 80.32 |
| 2 | fool | trickster_chaos | 62.75 |
| 3 | teenager | other | 50.28 |
| 4 | comedian | trickster_chaos | 50.01 |
| 5 | procrastinator | other | 48.61 |
| 6 | loner | grounded_social | 49.15 |
| 7 | smuggler | grounded_social | 47.81 |
| 8 | adolescent | other | 43.58 |
| 9 | robot | procedural_professional | 41.10 |
| 10 | luddite | grounded_social | 39.57 |

**Key observations:**
- `daredevil` (residual 80.32) is far outside any captured structure — extreme outlier in activation space, not explained by developmental, liminal, symbolic, or SVD coordinates
- `fool` (62.75) is the symbolic centroid's highest-similarity persona yet remains poorly explained — the fool activates differently than bard/sage despite semantic similarity
- `robot` (41.10) is a procedural_professional member with atypical activation geometry — likely a mechanical/nonhuman mode that doesn't fit adult human trait space
- `teenager` and `adolescent` persist despite being in the developmental centroid — the centroid partially explains them but not fully

### Best-explained personas in combined model

| Rank | Persona | Cluster | Combined residual |
|------|---------|---------|-----------------|
| 1 | producer | procedural_professional | 1.96 |
| 2 | reviewer | procedural_professional | 3.23 |
| 3 | accountant | editorial | 4.28 |
| 4 | paramedic | procedural_professional | 4.67 |
| 5 | engineer | procedural_professional | 4.80 |
| 6 | retiree | grounded_social | 5.35 |
| 7 | editor | editorial | 5.52 |

The procedural_professional and editorial clusters remain the most predictable after combining all features.

---

## 6. Summary Table

| Model | R² | Δ vs BigFive | PC1 | PC2 | PC3 | Splits |
|-------|-----|-------------|-----|-----|-----|--------|
| sem+BF (baseline) | 0.613 | — | 0.734 | 0.480 | 0.416 | 0/5 |
| sem+BF+centroids5 | 0.643 | +0.030 | 0.752 | 0.568 | 0.349 | 4/5 |
| sem+BF+SVD15 | **0.707** | **+0.094** | 0.819 | 0.585 | 0.528 | 5/5 |
| sem+BF+combined | 0.707 | +0.094 | 0.828 | 0.620 | 0.412 | 4/5 |

---

## 7. Interpretation

**What the residual manifold reveals:**

1. **Developmental/pre-adult structure** (toddler, infant, teenager, adolescent, caveman): These personas occupy an activation region that BigFive cannot describe because BigFive was designed for adult human personality. Their activation geometry may reflect a distinct "pre-socialized" or "low-metacognitive" mode in Qwen's representations.

2. **Collective/nonindividual agency** (swarm, hive, egregore, parasite, mycorrhizal): These personas have no individual trait profile. Their activation geometry may reflect network/distributed processing modes that Qwen represents as a distinct pole separate from individual-agent persona space.

3. **Symbolic/archetypal structure** (bard, sage, pirate, fool): Despite partial improvement from the symbolic centroid, `fool` and `comedian` remain hard. These may activate different modes than the interpretive/wisdom archetype (bard, sage). The fool/comedian operates through disruption and absurdity rather than meaning-making.

4. **Liminal/boundary-transgressive** (smuggler, daredevil, loner, exile): `daredevil` (residual 80.32) is the single hardest persona to explain after all features. It may represent an extreme pole in activation space that no current feature captures — possibly an intensity/risk-tolerance dimension orthogonal to both trait space and semantic space.

5. **SVD15 as a residual absorber**: SVD15 captures continuous prompt variation that neither cluster one-hots nor BigFive explain. Its high performance (5/5 splits) confirms that the no-label prompt corpus contains latent structure beyond the 7-cluster partition — but that structure is not yet interpretable from SVD components alone.

---

## 8. Artifact References

| Artifact | Path |
|----------|------|
| Full results JSON | `claude_residual_manifold_results.json` |
| Iteration log | `claude_residual_iteration_log.json` |
| Persona neighborhoods CSV | `claude_residual_persona_neighborhoods.csv` |
| Dimension codebook | `claude_residual_dimension_codebook.md` |
| Run script | `run_residual_manifold_analysis.py` |
| BigFive baseline | `../cross_model_feature_transfer/transfer_results.json` |
| Canonical PCA target | `../shared_latent_feature_benchmark/canonical_activation_pca3d.csv` |
