# Shared Latent-Feature Benchmark

Date: 2026-05-28
Analysis model: GPT-5.5 Standard
Script author model: GPT-5.5 Standard via Codex

## 1. Research Question

This benchmark aligns Codex/GPT-5.5 and Claude latent-feature analyses against the same persona rows, the same deterministic held-out splits, and the same metrics. The goal is to test whether Claude's Big Five result is target-specific or transfers to canonical activation geometry, and whether Codex's behavioral/procedural feature vocabulary transfers to Claude's cluster-cosine pseudo-PCA geometry.

## 2. Inputs and Alignment

- Common benchmark personas: 273
- Codex canonical activation personas available: 273
- Claude direct pseudo-PCA target rows available: 275
- Claude feature rows available: 275
- Claude pseudo-PCA target status: direct export from `claude_target_coordinates.csv`; no Big Five reconstruction was used.
- Canonical split set: the five deterministic Codex outer-loop seeds.

## 3. Feature Families

- Semantic baseline: 21 one-hot semantic-cluster features.
- Codex retained features: semantic baseline plus 31 retained outer-loop dimensions.
- Claude Big Five features: semantic baseline plus 5 Big Five columns from Claude's exported feature matrix.
- Claude full feature matrix: semantic baseline plus 55 Claude TF-IDF/Big-Five feature columns.
- Combined feature set: semantic baseline plus Codex retained dimensions plus Claude full feature matrix.

## 4. Results Matrix

| Feature set | Target | Mean R2 | Baseline R2 | Delta | PC1 | PC2 | PC3 | Residual reduction |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| semantic_baseline | canonical_activation_pca3d | 0.389 | 0.389 | +0.000 | 0.517 | 0.181 | 0.336 | +0.000 |
| codex_retained | canonical_activation_pca3d | 0.490 | 0.389 | +0.101 | 0.631 | 0.257 | 0.422 | +2.042 |
| claude_bigfive | canonical_activation_pca3d | 0.613 | 0.389 | +0.224 | 0.734 | 0.480 | 0.416 | +5.465 |
| claude_full_feature_matrix | canonical_activation_pca3d | 0.573 | 0.389 | +0.184 | 0.761 | 0.382 | 0.240 | +4.268 |
| combined_codex_claude | canonical_activation_pca3d | 0.585 | 0.389 | +0.196 | 0.757 | 0.352 | 0.391 | +4.571 |
| semantic_baseline | claude_cluster_cosine_pseudopca3d | 0.167 | 0.167 | +0.000 | 0.031 | 0.489 | 0.142 | +0.000 |
| codex_retained | claude_cluster_cosine_pseudopca3d | 0.166 | 0.167 | -0.001 | -0.047 | 0.629 | 0.244 | -0.019 |
| claude_bigfive | claude_cluster_cosine_pseudopca3d | 0.243 | 0.167 | +0.076 | 0.005 | 0.718 | 0.415 | +0.166 |
| claude_full_feature_matrix | claude_cluster_cosine_pseudopca3d | 0.153 | 0.167 | -0.014 | -0.142 | 0.731 | 0.278 | +0.063 |
| combined_codex_claude | claude_cluster_cosine_pseudopca3d | 0.150 | 0.167 | -0.017 | -0.141 | 0.727 | 0.281 | +0.026 |

## 5. Core Questions

### Does claude big five transfer to canonical activation pca

Yes. Big Five reaches R2 0.613 vs semantic baseline 0.389 (delta +0.224).

### Does codex retained transfer to claude pseudopca

No under the direct Claude target. Codex retained features reach R2 0.166 vs baseline 0.167 (delta -0.001).

### Does combined outperform either alone

On canonical activation PCA, combined R2 0.585 is not above the best single family (0.613). On Claude pseudo-PCA, combined R2 0.150 is not above the best single/full Claude family (0.243).

### Are codex and claude complementary

Mixed but not strongly complementary in this benchmark. Big Five carries strong transferable signal into canonical activation geometry, while Codex retained features do not improve the direct Claude pseudo-PCA target over the semantic baseline; combined features should be read as complementary only where held-out R2 and residual reduction both improve.

### Which target produces stronger agreement

Canonical activation PCA produces the cleaner cross-family comparison because neither feature family defines the target; Claude pseudo-PCA remains important but Big Five is close to a native positive-control target there.

### Which personas consistently well explained

teacher, veteran, guardian, void, novelist, influencer, provincial, scheduler

### Which personas consistently poorly explained

toddler, procrastinator, teenager, comedian, fool, infant, amateur, adolescent

### Does big five survive direct target alignment

Yes for canonical activation alignment: Big Five improves activation PCA by +0.224 R2 over semantic baseline.

### Does trait plus procedural interpretation survive

Supported as a bounded interpretation: trait-style and procedural/behavioral features both carry predictive signal, but neither should be treated as final or causal.

## 6. Most and Least Explained Personas

Using the combined feature set on canonical activation PCA, the most effectively explained personas are: teacher, veteran, guardian, void, novelist, influencer, provincial, scheduler, ghost, witness.

Using the same condition, the least effectively explained personas are: toddler, procrastinator, teenager, comedian, fool, infant, amateur, adolescent, gamer, hoarder. These are diagnostic residual cases for the current feature vocabulary, not evidence that the personas are inherently inexplicable.

## 7. Interpretation

The shared benchmark supports a mixed but productive alignment story. Big Five-style features survive direct alignment to canonical activation PCA, which means Claude's trait result is not merely an artifact of its pseudo-PCA target. Codex procedural/behavioral dimensions do not transfer to Claude's direct pseudo-PCA export over the semantic baseline in this aligned run. The combined feature family is useful as an empirical diagnostic, but any trait-plus-procedural interpretation should remain bounded to held-out prediction rather than promoted to a causal explanation.

## 8. Limitations

- Claude's pseudo-PCA target is a direct export, but it remains a 7-cluster-cosine pseudo-target rather than the full activation PCA target.
- Feature matrices are fixed at the common persona intersection to support apples-to-apples comparison.
- Cluster accuracy is secondary and only reported for canonical activation clusters.
- No pods, activations, or model calls were run.

## 9. Recommended Next Steps

- Ask Claude to run the same shared benchmark script or consume these exported matrices so both agents report against identical files.
- Add a blinded human-readable feature codebook for Codex dimensions and Claude Big Five columns.
- Re-run the benchmark after any future no-label activation stress test to see whether trait/procedural transfer survives label removal.