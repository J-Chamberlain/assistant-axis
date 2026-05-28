# Claude Residual Dimension Codebook

**Date:** 2026-05-28
**Analysis:** Claude residual manifold analysis (after BigFive)
**Method:** Reference persona centroid cosine similarity features

Each feature = cosine similarity between a persona's concatenated no-label prompts
(TF-IDF, ngram 1-2, max_features=8000, sublinear_tf) and the mean TF-IDF vector
of the listed anchor personas. Range: [0, 1], typical max ~0.55–0.65.

---

## sim_to_developmental

**Anchor personas:** toddler, infant, teenager, adolescent, caveman

**Captures:** Pre-adult or pre-socialized cognitive modes. Personas whose prompts emphasize
nascent identity formation, limited metacognitive capacity, emotional volatility, or
primitive/primal existence prior to adult socialization structures.

**Top scorers (non-anchor):** No non-anchor personas score above 0.2; falloff is sharp.
Adjacent: immature, student (marginally).

**Activation interpretation:** The developmental/other cluster is the hardest to explain
with BigFive traits, likely because BigFive was designed for adult human personality.
These personas may activate a distinct "pre-metacognitive" or "embodied primal" mode
in Qwen's representation.

**PC connection:** Improves PC2 (+0.088 over baseline), confirming these personas
distort the social/relational axis most.

---

## sim_to_stalling

**Anchor personas:** procrastinator, hoarder, amateur, student

**Captures:** Low-agency passive or accumulation modes. Personas whose prompts
emphasize avoidance, delay, uncommitted interest, or non-expert engagement without
professional formation. Not pathological — hoarder and amateur reflect casual
enthusiasm and object-relation rather than pure avoidance.

**Top scorers (non-anchor):** competitor (0.111), novice-adjacent personas.

**Activation interpretation:** These personas may activate a "low-directed-agency"
mode distinct from both professional competence and adversarial/disruptive postures.
Procrastinator (residual 48.61 even after all features) remains hardest to explain —
possibly because its activation reflects a specific behavioral pattern not captured
by semantic proximity to stalling vocabulary.

---

## sim_to_collective

**Anchor personas:** swarm, hive, egregore, parasite

**Captures:** Non-individual, distributed, or parasitic entity modes. Personas whose
prompts explicitly describe multi-body collective consciousness, hive-mind coordination,
or biological dependency on a host. Sharp falloff — mycorrhizal (0.176) is the only
non-anchor persona with meaningful score.

**Top scorers (non-anchor):** mycorrhizal (0.176), leviathan (adjacent).

**Activation interpretation:** Collective entities have no individual trait profile.
Their activation geometry likely reflects a distinct "distributed agent" mode that
Qwen encodes differently from all individual persona representations. The sharp
centroid boundary (max non-member 0.176 vs member minimum 0.475) confirms this
is a tight semantic cluster in no-label prompt space.

---

## sim_to_symbolic

**Anchor personas:** bard, sage, pirate, fool

**Captures:** Symbolic/archetypal cultural roles with mythic or traditional function.
Personas whose prompts draw on timeless archetypes, oral tradition, wisdom-keeper,
or iconic cultural identities rather than professional or psychological descriptions.

**Top scorers (non-anchor):** guru (0.184), oracle (adjacent).

**Activation interpretation:** The symbolic centroid captures bard, sage, and pirate
well, but fool (residual 62.75) and comedian (50.01) remain hard — suggesting that
the disruptive/absurdist mode of symbolic roles activates differently from the
wisdom/narrative mode. Fool may represent a distinct adversarial-absurd pole rather
than a symbolic-archetypal one.

**Note:** Despite high centroid similarity, fool is the second-worst-explained persona
in the combined model — centroid similarity is necessary but insufficient.

---

## sim_to_liminal

**Anchor personas:** smuggler, exile, loner, daredevil

**Captures:** Boundary-transgressive, marginalized, or outside-society roles. Personas
whose prompts describe operation outside normal social structures, voluntary or
involuntary social exclusion, or high-risk freedom-seeking behavior.

**Top scorers (non-anchor):** hermit (0.145), maverick (adjacent).

**Activation interpretation:** Liminal roles cluster semantically but show large
variation in activation residuals — smuggler (47.81), loner (49.15), and daredevil
(80.32) all remain high after all features. Daredevil is the single hardest persona
to explain in the full dataset (residual 80.32), suggesting it occupies an extreme
activation pole that no current feature describes. Its liminal similarity (0.551)
is the highest of any non-anchor, yet it remains unpredicted — the activation pattern
may reflect an intensity/agency dimension orthogonal to semantic features.

---

## SVD15 Components (non-interpretable)

The TF-IDF SVD15 features (svd_0 through svd_14) capture continuous semantic
variation in no-label prompt space with 13.8% explained variance. These components
are not individually interpretable but carry substantial activation prediction signal
(+0.094 R² over BigFive alone, 5/5 splits).

The SVD components likely capture:
- Formality and register variation across prompts
- Domain-specific vocabulary clusters (professional, fantastical, social, technical)
- Syntactic and structural patterns in how different personas are described
- Cross-cluster bridges not captured by the k=7 hard partition

SVD15 outperforms the 5 interpretable centroids (+0.094 vs +0.030) and adding
centroids to SVD15 adds no marginal signal — centroids are largely spanned by the
SVD component space. SVD15 is the better predictive model; centroids are the better
interpretive model.
