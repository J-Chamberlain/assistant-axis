# Claude Feature Dimension Codebook

## Provenance
- analysis_model: claude-sonnet-4-6
- script_author_model: claude-sonnet-4-6
- date: 2026-05-28

## Best Feature Set Used in Claude Loop
F1: TF-IDF (SVD-50 components) + BigFive (5 ordinal dims) = 55 total features

---

## Block 1: TF-IDF Semantic Features (tfidf_svd_00 … tfidf_svd_49)

Source: no-label rewritten prompts (first prompt per role, from
  research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl)

Method: TF-IDF (unigrams, custom stopwords) → SVD(n_components=50, random_state=42)
  → L2-normalized token frequencies × IDF weights → truncated SVD
Interpretability: None. SVD components are not interpretable on their own.
Role in loop: Semantic baseline (Round 0). Captures prompt vocabulary variation.

---

## Block 2: BigFive Psychological Traits (big5_agreeableness … big5_openness)

Source: visualizations/bigfive_profiles.json
  275 roles × 5 dimensions, ordinal scale 1–5

Dimensions:
  big5_agreeableness    — Agreeableness (1=low, 5=high)
  big5_conscientiousness — Conscientiousness (1=low, 5=high)
  big5_extraversion     — Extraversion (1=low, 5=high)
  big5_neuroticism      — Neuroticism (1=low, 5=high)
  big5_openness         — Openness (1=low, 5=high)

IMPORTANT PROVENANCE NOTE:
  These scores were assigned by an LLM (likely Claude or GPT-4) during the
  original Paper 1 analysis, not by human raters or empirical measurement.
  They encode the assigning model's implicit stereotypes about role personality.
  Strong BigFive predictability may reflect model-prior alignment rather than
  genuine psychological structure in the activation geometry.

Role in loop: Added in Round 1. Produced the largest single improvement (+0.219 PCA3D R²).

---

## Block 3: DarkTriad Traits (NOT in best model; tested in Round 2)

Source: visualizations/dark_triad_profiles.json
  Same provenance caveat as BigFive.

Dimensions:
  dark3_machiavellianism — Machiavellianism (1–5)
  dark3_narcissism       — Narcissism (1–5)
  dark3_psychopathy      — Psychopathy (1–5)

Round 2 result: PCA3D R²=0.353, Δ-0.009. NOT retained.

---

## Block 4: Semantic Cluster One-Hot (NOT in best model; tested in Round 3)

Source: deep_semantic_topology_analysis.json → no_label_k7_clusters
  7 clusters from no-label prompt TF-IDF/SVD + k-means (deterministic).

Round 3 result: PCA3D R²=0.339, Δ-0.014. NOT retained.

---

## Blocks 5–6: Anchor/Bridge + Claude Hypotheses + Cross-Model Rank
Not tested (plateau triggered before these rounds).

---

## Target Variables

### Pseudo-PCA3D (primary target)
Source: research/cluster_analysis/qwen_cluster_directionality.csv
  275 × 7 cosine distances to named Qwen cluster centroids:
  cos_to_editor, cos_to_synthesizer, cos_to_blogger, cos_to_ancient,
  cos_to_trickster, cos_to_contrarian, cos_to_podcaster

Method: StandardScaler → PCA(n_components=3, random_state=42)
  PC1: 59.3% EV | PC2: 25.9% | PC3: 10.3% | Total: 95.5%

CRITICAL NOTE FOR CODEX TRANSFER:
  This is NOT Codex canonical activation PCA. Codex's target is presumably
  PCA on the full Qwen role-vector activation tensors. This proxy uses only
  7 named cluster centroids. PC1 of this proxy may differ in meaning and
  orientation from PC1 of the full Qwen activation space.
  Transfer testing required before conclusions generalize.

### Gemma Axis (secondary target)
Source: visualizations/full_ranking.csv → axis_projection_layer22
  Normalized to [-1, 1]: y = 2*(x - min)/(max - min) - 1

---

## CV Protocol
  StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
  Stratification: Gemma activation cluster label (7 classes)
  Regression: Ridge(alpha=1.0) with StandardScaler per fold
  Metric: mean held-out R² across PC1, PC2, PC3
