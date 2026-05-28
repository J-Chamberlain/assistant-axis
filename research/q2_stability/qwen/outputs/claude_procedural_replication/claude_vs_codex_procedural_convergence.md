# Claude vs Codex: Procedural Replication Convergence Analysis

**Date:** 2026-05-28
**analysis_model:** claude-sonnet-4-6
**Target:** Canonical Qwen activation PCA3D (N=273 personas, same shared benchmark splits)
**Constraint:** Claude constrained to 20 procedural/operating-mode dimensions, no BigFive.

---

## Scorecard

| Metric | Claude Procedural | Codex Procedural | BigFive (ceiling) |
|---|---|---|---|
| Feature vocabulary | 20 procedural operating modes | 31 behavioral/motivational dims | 5 psychological traits |
| Retained dims | 3 | 31 | 5 |
| Mean PCA3D R² | **0.4139** | **0.4901** | **0.6130** |
| Delta vs baseline | +0.0245 | +0.1007 | +0.2236 |
| PC1 R² | 0.541 | 0.631 | 0.734 |
| PC2 R² | 0.195 | 0.257 | 0.480 |
| PC3 R² | 0.380 | 0.422 | 0.415 |
| Mean residual | 26.72 | 25.17 | ~21.7 |
| Iterations to plateau | 3 | 4 | N/A |
| Best-explained cluster | procedural_professional | procedural_professional | procedural_professional |
| Worst-explained cluster | other/developmental | other/developmental | other/developmental |

---

## Qualitative Convergence

### 1. First retained dimension family: CONVERGENT

**Claude retained:** evaluation (judge, verify, audit, screen, review, grade)
**Codex retained in iteration 1:** `evaluate_judge_verify` — "Evaluation, judgment, verification, screening, correction, review, or auditing"

This is the clearest cross-model convergence finding. Both models, using different vocabularies
and operationalization methods, independently identified evaluation as the primary procedural
dimension explaining activation geometry beyond semantic baselines.

### 2. Second retained family: CONVERGENT (care/guidance)

**Claude retained:** guidance + care (positive-service triad with evaluation)
**Codex retained in iteration 1:** `cooperative_care` — "Cooperation, care, trust, reciprocity, support, guidance, or nurturing"

Codex merged care and guidance into a single cooperative-care dimension. Claude split them, but
both appear in Claude's first retained bundle. The convergence is that both models identify
positive-service operating modes (evaluation/care/guidance) as the dominant explanatory triad.

### 3. Adversarial/destabilizing dimensions: PARTIAL DIVERGENCE

**Claude:** destabilization, disruption, coercion — all discarded (F3 bundle had negative delta)
**Codex:** `destabilize_expose_disrupt`, `reactive_opposition`, `adversarial_dominance` — all retained

Codex retains adversarial/destabilizing dimensions because its simultaneous 31-dim optimization
allows regularization to balance positive and adversarial modes. Claude's iterative sequential
search discards these when added after the positive-service triad. Under Claude's operationalization,
adversarial keywords are too sparse and noisy to add signal above an already-anchored model.

**Interpretation:** This is an artifact of operationalization sparsity (manipulation: 9/273 personas),
not a genuine disagreement about whether adversarial dimensions exist. Codex's richer vocabulary
captures adversarial roles more reliably.

### 4. Cluster-level best/worst personas: STRONGLY CONVERGENT

**Both models worst-explained:** procrastinator, toddler, teenager, adolescent, infant, sage, bard
**Both models best-explained:** screener/grader/editor (editorial cluster), mediator/analyst/teacher
                                  (procedural_professional cluster)

6/15 worst-explained personas overlap exactly (from Claude's earlier BigFive analysis).
Procedural operationalization does not resolve the developmental/other cluster residual problem.

---

## Quantitative Divergence Analysis

### Why Codex R²=0.490 > Claude R²=0.414

**Gap:** -0.076 (Claude procedural is below Codex by ~7.6 percentage points)

**Primary cause: keyword ceiling**
All 20 Claude procedural dims simultaneously yield R²=0.4148 — nearly identical to the 3 retained.
This means the 20-dim vocabulary has a representational ceiling around 0.41–0.42. Adding more dims
from the same keyword vocabulary doesn't improve prediction; the signal is saturated by 3 dims.

**Secondary cause: vocabulary richness**
Codex's 31 dimensions were derived iteratively from the full prompt corpus and include finer-grained
distinctions (e.g., `boundary_liminal_instability`, `semantic_label_dependence_risk`,
`standards_and_error_aversion`) that Claude's keyword patterns don't capture. These dimensions
explain variance within the procedural cluster that general keyword matching misses.

**Third cause: sparse adversarial coverage**
Claude's adversarial dims (manipulation: 9/273, persuasion: 23/273, exposure: 21/273) have very
low coverage. Codex's equivalent dims likely have better operationalization for roles like
trickster, contrarian, provocateur, and villain.

---

## Interpretation

Claude independently converged on the same **qualitative procedural structure** as Codex:
- Evaluation/verification is the primary axis
- Care and guidance form the positive-service triad
- Procedural_professional cluster is most predictable
- Developmental/other cluster is least predictable

Claude did **not** match Codex's **quantitative performance** under keyword-based procedural
operationalization. The gap (R²=0.414 vs 0.490) reflects vocabulary ceiling, not disagreement
about which kinds of procedures matter.

**The most robust cross-model convergence finding from this analysis:**
*Evaluation operating mode (judge/verify/audit/screen) is the primary procedural dimension
explaining canonical Qwen activation geometry beyond semantic cluster baselines. This finding
emerged independently from both Claude and Codex under different iterative optimization regimes,
different vocabularies, and different implementation approaches.*

---

## Limitations

1. **Keyword sparsity**: Most procedural dims have low nonzero coverage (manipulation 3%, persuasion 8%).
   A richer operationalization (e.g., using LLM-scored profiles rather than keyword matching) would
   likely push the procedural ceiling above 0.42.

2. **Sequential vs simultaneous optimization**: Claude used sequential bundle addition; Codex used
   simultaneous optimization over 31 dims with kfold alpha selection. This changes what gets retained.

3. **No BigFive allowed**: Blocking BigFive from Claude's search while Codex can include BigFive-adjacent
   dimensions (emotional regulation, assistant adjacency) is an asymmetric constraint.

4. **All-20 ceiling test**: The near-identical R² for 3 retained vs all 20 dims (0.4139 vs 0.4148)
   suggests severe multicollinearity — many procedural dims are near-synonyms under keyword scoring.
