# Claude Latent Feature Loop — Export Manifest

**Date:** 2026-05-28
**Purpose:** Enable Codex/GPT-5.5 apples-to-apples transfer comparison
**analysis_model:** claude-sonnet-4-6
**Branch:** claude/persona-inventory-topology-4qp10

---

## Files in This Directory

### Analysis scripts
| File | Description |
|---|---|
| run_claude_latent_feature_loop.py | Full iterative loop (re-run to reproduce) |
| export_claude_inputs.py | This script — exports clean CSVs for Codex |

### Result artifacts
| File | Rows | Cols | Description |
|---|---|---|---|
| claude_feature_matrix.csv | 275 | 56 | persona + 50 TF-IDF + 5 BigFive (best model input) |
| claude_target_coordinates.csv | 275 | 14 | persona + pseudo-PC1/2/3 + Gemma proj + 7 cosines + cluster |
| claude_split_assignments.csv | 275 | 13 | persona + fold ID + predictions + actuals + residuals |
| claude_pca_loadings.csv | 3 | 9 | PCA component vectors (to project new data onto same space) |
| claude_dimension_codebook.md | — | — | Full feature definitions with provenance |
| claude_persona_explanation_rankings.csv | 275 | — | Persona ranked by final residual (from loop) |
| claude_persona_explanation_rankings.json | 275 | — | Same with provenance metadata |
| claude_latent_feature_loop_report.md | — | — | Narrative loop report |
| claude_latent_feature_loop_master_log.json | — | — | Machine-readable loop summary |
| claude_vs_codex_latent_feature_comparison.md | — | — | Comparison template (Codex column blank) |

---

## Key Results (for Codex context)

| Metric | Value |
|---|---|
| Null PCA3D R² (permutation, n=200) | -0.322 mean, -0.221 p95 |
| Semantic baseline (TF-IDF only) | 0.142 |
| Best model (TF-IDF + BigFive) | **0.361** |
| Improvement over baseline | +0.219 |
| PC1 held-out R² | -0.089 (UNPREDICTED) |
| PC2 held-out R² | 0.732 |
| PC3 held-out R² | 0.440 |
| Gemma axis held-out R² | 0.695 |
| Loop plateau | Round 3 (DarkTriad and semantic cluster add no signal) |
| Retained feature sets | TF-IDF (50 SVD dims) + BigFive (5 dims) |

---

## Target Compatibility Warning

Claude used **pseudo-PCA3D** derived from the 275×7 Qwen cluster-cosine matrix.
This is NOT identical to Codex's canonical activation PCA target (if Codex used
full Qwen role-vector tensors). Differences to expect:

1. **PC orientation** may differ. The pseudo-PCA is over 7 named centroid directions;
   the full activation PCA is over thousands of dimensions.
2. **PC1 meaning** may differ. Claude's PC1 (59% EV, unpredicted) may or may not
   correspond to Codex's PC1.
3. **Variance explained** may differ. Claude's target has 95.5% EV in 3 PCs because
   the input is already low-dimensional.

For a fair comparison, Codex should either:
  (a) Also predict Claude's pseudo-PCA3D targets (files provided here), OR
  (b) Provide its PCA target coordinates so Claude's features can be tested on them.

The `claude_target_coordinates.csv` contains all 7 raw Qwen cosines per persona,
which Codex can use to re-derive the pseudo-PCA3D independently and confirm matching.
The `claude_pca_loadings.csv` contains the PCA component vectors for exact replication.

---

## What Codex Needs for Transfer Comparison

- [x] Feature matrix: claude_feature_matrix.csv (BigFive columns clearly labeled)
- [x] Target coordinates: claude_target_coordinates.csv (pseudo-PCA3D + raw cosines)
- [x] Split assignments: claude_split_assignments.csv (same folds for matched comparison)
- [x] PCA loadings: claude_pca_loadings.csv (project onto same pseudo-PCA space)
- [x] Feature definitions: claude_dimension_codebook.md
- [ ] Codex target coordinates: NEEDED FROM CODEX (full activation PCA, if different)
- [ ] Codex feature matrix: NEEDED FROM CODEX (for Claude-side transfer test)

---

## Raw GitHub URLs (branch: claude/persona-inventory-topology-4qp10)

BASE = https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/claude/persona-inventory-topology-4qp10/research/q2_stability/qwen/outputs/claude_latent_feature_loop/

Files:
  claude_feature_matrix.csv
  claude_target_coordinates.csv
  claude_split_assignments.csv
  claude_pca_loadings.csv
  claude_dimension_codebook.md
  claude_feature_export_manifest.md
  claude_vs_codex_latent_feature_comparison.md
  claude_latent_feature_loop_report.md
  claude_latent_feature_loop_master_log.json
  claude_persona_explanation_rankings.csv
