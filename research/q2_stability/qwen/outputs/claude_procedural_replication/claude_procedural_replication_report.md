# Claude Procedural Replication Report

**Date:** 2026-05-28
**analysis_model:** claude-sonnet-4-6
**Constraint:** Procedural/operating-mode ontology only. No BigFive, no trait labels.
**Target:** Canonical Qwen activation PCA3D (shared benchmark, N=273 personas, 5 splits)
**Evaluation:** Exact replication of shared benchmark protocol (joint R², kfold alpha, custom ridge)

---

## Research Question

Can Claude independently rediscover procedural geometry when constrained to operate exclusively
within a 20-dimension operating-mode ontology (no BigFive, no personality-trait terminology)?

**Answer: Yes for qualitative structure. No for quantitative parity with Codex.**

---

## Results Summary

| Condition | Mean PCA3D R² | Delta vs Baseline | Delta vs Codex |
|---|---|---|---|
| Semantic baseline | 0.3894 | +0.000 | -0.101 |
| Claude procedural final (3 dims) | 0.4139 | +0.025 | -0.076 |
| Claude procedural ceiling (all 20 dims) | 0.4148 | +0.025 | -0.075 |
| Codex procedural (31 dims) | 0.4901 | +0.101 | ±0.000 |
| BigFive ceiling (reference) | 0.6130 | +0.224 | +0.123 |

---

## Iteration Progression

| Iter | Bundle | Dims | R² | Delta | Decision |
|---|---|---|---|---|---|
| 0 (baseline) | semantic | 21 one-hot | 0.3894 | — | — |
| 1 | F1_eval_guide_care | eval + guidance + care | 0.4139 | +0.0245 | **retained** |
| 2 | F2_enforce_coord_optim | enforcement + coord + optim | 0.4204 | +0.0065 | discarded |
| 3 | F3_destab_disrupt_coerce | destab + disrupt + coerce | 0.4080 | -0.0059 | discarded |

Plateau triggered after iteration 3 (2 consecutive non-improving iterations).

---

## Per-Axis Results (Final Model)

| Axis | Claude Procedural | Codex Procedural | BigFive |
|---|---|---|---|
| PC1 | 0.541 | 0.631 | 0.734 |
| PC2 | 0.195 | 0.257 | 0.480 |
| PC3 | 0.380 | 0.422 | 0.415 |
| **Mean (joint R²)** | **0.414** | **0.490** | **0.613** |

PC2 is the weakest axis for Claude procedural — operating-mode keywords capture social/interpersonal
variance poorly. BigFive's +0.285 PC2 advantage shows that trait-like variation (not just procedure)
dominates the secondary activation direction.

---

## Retained Dimensions

### 1. evaluation
Detection of assessing, judging, verifying, screening, reviewing, grading, auditing.
104/273 personas (38%). This is the highest-coverage procedural dimension and the primary
explanatory axis. Strongly overlaps with the editorial activation cluster and the evaluative
pole of PC1.

### 2. guidance
Detection of teaching, mentoring, coaching, advising, instructing, leading toward understanding.
93/273 personas (34%). Complements evaluation by capturing knowledge-transmission and development
roles, which are semantically distinct but geometrically adjacent.

### 3. care
Detection of nurturing, supporting, healing, comforting, aiding, tending to wellbeing.
87/273 personas (32%). Forms the positive-service triad with evaluation and guidance. Adds marginal
PC3 prediction improvement; reflects the cooperative-care structure of the grounded_social cluster.

---

## Key Finding: Vocabulary Ceiling

Running all 20 procedural dimensions simultaneously (R²=0.4148) barely exceeds the 3 retained
dimensions (R²=0.4139). This is the most important methodological finding:

**The 20-dimension procedural vocabulary, under keyword-based operationalization from no-label
prompts, has a representational ceiling at R²≈0.41–0.42.**

This ceiling is not caused by multicollinearity alone (the retained 3 are distinct). It reflects
that keyword matching on no-label prompts cannot fully operationalize the procedural structure
that Codex captures through richer corpus analysis. The gap to Codex (0.490) is an operationalization
gap, not a theoretical gap about what procedural dimensions matter.

---

## Best and Worst Explained Personas

### Best (lowest residual, well-explained by procedural model)
1. screener (editorial) — 3.20
2. mediator (procedural_professional) — 5.30
3. teacher (procedural_professional) — 5.60
4. veterinarian (procedural_professional) — 5.84
5. grader (editorial) — 6.78
6. analyst (procedural_professional) — 7.00
7. playwright (grounded_social) — 7.97
8. familiar (mythic_spiritual) — 8.21
9. assistant (procedural_professional) — 8.82
10. futurist (procedural_professional) — 8.85

These roles have legible, unambiguous procedural profiles: evaluation for screener/grader,
guidance+care for teacher, evaluation for analyst. The procedural model places them accurately.

### Worst (highest residual, poorly explained by procedural model)
1. procrastinator (other) — 76.18
2. smuggler (grounded_social) — 65.67
3. sage (mythic_spiritual) — 65.34
4. toddler (other) — 64.12
5. teenager (other) — 63.61
6. adolescent (other) — 63.50
7. bard (mythic_spiritual) — 63.47
8. cyborg (procedural_professional) — 59.37
9. bartender (grounded_social) — 58.34
10. infant (other) — 55.83

Developmental roles (toddler, teenager, adolescent, infant) remain worst-explained — same finding
as BigFive analysis. The procedural model also fails on: sage (wisdom without specific procedure),
bard (performance without procedure), smuggler (ambiguous between coercion and disruption),
cyborg (technological identity without legible operating mode), bartender (hospitality that doesn't
fit any single procedural mode cleanly).

---

## Comparison with Codex Procedural Structure

**Convergence:**
- Both independently selected evaluation as the primary retained dimension
- Both identified care/cooperative-care as a retained positive-service dimension
- Both identified procedural_professional as best-explained cluster
- Both identified developmental/other as worst-explained cluster
- Both plateaued after 3–4 iterations

**Divergence:**
- Codex retained 31 dims vs Claude 3 (vocabulary richness)
- Codex R²=0.490 vs Claude R²=0.414 (quantitative gap)
- Codex retains adversarial/destabilizing dims; Claude discards them (operationalization sparsity)
- Codex captures finer distinctions (semantic_label_dependence, boundary_liminal_instability)
  that Claude's keyword vocabulary misses

**Strongest convergence finding:**
*Evaluation operating mode (judge/verify/audit/screen) is the primary procedural explanatory axis
for canonical Qwen activation geometry. This emerged independently from both models under different
constraints.*

---

## Interpretation Under Procedural Constraint

Within the procedural/operating-mode ontology:

1. Activation geometry is organized first by **who is doing what function** (evaluation, guidance,
   care) rather than **what kind of entity they are** (personality type, social identity, mythology).

2. The evaluative operating mode — assessment, verification, quality control — is not arbitrary.
   It corresponds directly to the Gemma assistant axis finding (proofreader, screener, grader
   at the positive pole). This convergence across models and across operating-mode constraints
   is a robust finding.

3. Developmental roles are not well-characterized by any procedural vocabulary. They occupy
   activation positions that are not defined by what they DO but by what they ARE (stages of
   development, age-indexed social positions). This supports the convergent interpretation from
   BigFive and Codex analyses: developmental personas are the "other" cluster in every vocabulary.

4. The care+guidance dyad explains grounded_social cluster placement better than evaluation alone,
   but neither dimension captures the mythic_spiritual or trickster_chaos cluster well. Those
   clusters may require symbolic or theatrical procedural vocabularies beyond the 20 allowed here.

---

## Methodological Notes

1. **Keyword scoring**: scored 0–3 per persona from concatenated no-label prompts (5 per role).
   No role label exposure in source text.

2. **Exact shared benchmark protocol**: joint multi-output R², kfold alpha selection from
   [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0], custom ridge with bias term and pinv.

3. **Calibration confirmed**: semantic baseline R²=0.3894 (matches shared benchmark to 4 decimal
   places). BigFive ceiling R²=0.6130 (matches shared benchmark 0.612979 to 4 decimal places).

4. **Ceiling test**: All 20 dims simultaneously = R²=0.4148 ≈ 3 retained dims (0.4139).
   This rules out vocabulary size as the limiting factor; the keyword operationalization itself
   is the ceiling.

5. **No pods, no new inference, no activations generated.** All features derived from existing
   no-label prompts (research/assistant_axis_methodology/no_label_prompt_ablation/).

---

## Artifacts

| File | Description |
|---|---|
| `claude_procedural_replication_results.json` | Machine-readable results, all metrics |
| `claude_procedural_iteration_log.json` | Per-iteration decisions and rationales |
| `claude_procedural_persona_residuals.csv` | Per-persona final residual rankings |
| `claude_procedural_dimension_codebook.md` | Full dimension definitions and coverage |
| `claude_vs_codex_procedural_convergence.md` | Cross-model qualitative and quantitative comparison |
| `run_procedural_replication.py` | Reproducible Python script |
