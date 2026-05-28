# Claude vs Codex/GPT-5.5 Latent Feature Comparison

**Date:** 2026-05-28
**analysis_model:** claude-sonnet-4-6
**script_author_model:** claude-sonnet-4-6
**orchestration_agent:** claude-code
**provider:** anthropic

---

## Status of Codex/GPT-5.5 Results

The Codex/GPT-5.5 latent feature loop reports referenced in the task specification
(`latent_feature_discovery_loop_report.md`, `framing_ablation_report.md`,
`iterative_outer_loop_report.md`, `outer_loop_master_log.json`) were **not found in
the current repository clone**. They may exist on the Mac Mini but have not been
committed. Direct numerical comparison is therefore not possible in this session.

This document records the Claude-side results in the format that comparison would
require, and states what convergence or divergence would be interpretively significant.

## Export Status (updated 2026-05-28)

All Claude-side inputs and outputs are now exported in clean CSVs for Codex transfer
comparison. See `claude_feature_export_manifest.md` for full file inventory.

Key transfer note: Claude's target is **pseudo-PCA3D** from the 275×7 Qwen
cluster-cosine matrix, which is a proxy for — but not identical to — the full Qwen
activation-space PCA. Codex should either (a) predict Claude's pseudo-PCA3D targets
using `claude_target_coordinates.csv`, or (b) provide its own activation PCA
coordinates so Claude's BigFive features can be tested on the canonical target.
The BigFive finding (R²=0.361, Gemma axis R²=0.695) should be preserved as a
valid target-specific result pending transfer testing against Codex's canonical target.

---

## Claude-Side Results Summary

| Metric | Value |
|---|---|
| Null PCA3D R² (permutation mean) | -0.3219 |
| Null PCA3D R² p95 | -0.2210 |
| Baseline (TF-IDF) PCA3D R² | 0.1423 |
| Best model (TF-IDF + BigFive) PCA3D R² | 0.3611 |
| Improvement over baseline | +0.219 |
| PC1 held-out R² | -0.089 (UNPREDICTED) |
| PC2 held-out R² | 0.732 |
| PC3 held-out R² | 0.440 |
| Gemma axis held-out R² | 0.695 |
| Best feature set | F1: TF-IDF + BigFive |
| Plateau triggered at | Round 3 (DarkTriad and semantic cluster add no signal) |

Target: Pseudo-PCA3D from 275×7 Qwen cluster-cosine matrix
(PC1: 59.3% variance, PC2: 25.9%, PC3: 10.3% — total 95.5%)

---

## Claude's Independent Feature Hypotheses

Claude independently proposed ten semantic dimensions as likely explanatory of
activation cluster structure. These were derived from persona names, no-label
prompts, and prior semantic topology findings — not from activation labels:

1. **evaluative_orientation** — 15/275 roles (5%): assessment/quality-control function
2. **relational_embodiment** — 66/275 roles (24%): social position or lived experience identity
3. **mythic_symbolic** — 43/275 roles (16%): non-ordinary ontological category
4. **adversarial_oppositional** — 15/275 roles (5%): challenge/disruption stance
5. **creative_narrative** — 18/275 roles (7%): artistic creation or storytelling function
6. **professional_specialist** — 46/275 roles (17%): domain-expert professional
7. **abstract_collective** — 26/275 roles (9%): non-individual entity
8. **pedagogical_knowledge** — 47/275 roles (17%): knowledge transmission function
9. **hedonistic_leisure** — 28/275 roles (10%): pleasure or leisure orientation
10. **moral_ideological** — 20/275 roles (7%): strong ethical/ideological commitment

These dimensions were **not reached** in the iterative loop because plateau triggered
before them. DarkTriad and semantic cluster (rounds 2-3) both produced marginal
decreases in held-out R², stopping the loop. This does not mean Claude's hypothesized
dimensions carry zero signal — it means they add nothing above BigFive + TF-IDF on
this target with N=275.

---

## Primary Findings from Claude Analysis

### Finding 1: BigFive dominates as the explanatory framework

BigFive traits alone (added to TF-IDF) explain 36.1% of pseudo-PCA3D variance,
against a -32.2% null and 14.2% TF-IDF baseline. The improvement (+21.9 points)
is substantial and well above the permutation p99 threshold.

This is consistent with the confirmed finding that Conscientiousness correlates at
r=0.792 with the Gemma assistant axis (Paper 1). Claude independently arrived at
a framework that reproduces this psychological-structure interpretation.

### Finding 2: PC1 is unpredictable from both semantic features and BigFive

The first principal component of the Qwen cluster-cosine matrix (59.3% of variance)
has held-out R² = -0.089 under the best model. This is the single most important
structural finding: the dominant activation dimension is not predictable from
prompt semantics or human psychological profiles.

Interpretation: Qwen's PC1 may capture something about the model's internal
organization of role representations that is orthogonal to human-legible
psychological categories. This is a hypothesis, not a confirmed finding.

Alternatively: PC1 may correspond to the assistant axis itself (high
assistant-axis projection = strong cosine to all centroids), which would be
circularly auto-predictable from activation labels but not from semantic features.
This interpretation requires direct inspection of Qwen axis alignment with PC1.

### Finding 3: PC2 and PC3 are well-predicted by BigFive

PC2 R² = 0.732, PC3 R² = 0.440 under BigFive + TF-IDF. These are substantive
predictive gains. The dimensions of human variation captured in BigFive profiles
correspond to real structure in the Qwen activation cosine space — but only for
the secondary and tertiary principal components.

### Finding 4: "Other" cluster is systematically worst-explained

The top 8 worst-explained personas are: toddler, caveman, infant, pirate,
proofreader, teenager, perfectionist, poet. The "other" cluster (developmentally
specific, ontologically unusual, or contradictory roles) is systematically
mislocated by BigFive. Reasons:

- Developmental stages (toddler, infant, adolescent, teenager, caveman) do not have
  coherent BigFive profiles — they are identity positions rather than trait profiles.
- Proofreader is the top-ranked editorial role in Gemma's axis but has a Qwen
  cluster-cosine profile that makes it an extreme outlier in Qwen's PC space.
- Poet and amnesiac may represent roles whose activation geometry is driven by
  narrative and experiential content that BigFive doesn't capture.

### Finding 5: Procedural-professional is best-explained

The top 15 best-explained personas are dominated by procedural_professional archetypes
(architect, journalist, paramedic, marketer, doctor, researcher, recruiter) plus a
few grounded_social roles (veteran, soldier) and trickster roles (improviser,
absurdist). These roles have stereotyped, recognizable BigFive profiles that map
cleanly to Qwen's cluster cosine structure.

---

## Cross-Model Comparison Template

The following table shows what should be compared when Codex results become available.
Each cell records what Claude found; the Codex column should be filled with Codex results.

| Comparison dimension | Claude (this analysis) | Codex/GPT-5.5 |
|---|---|---|
| Primary target | Pseudo-PCA3D from Qwen cosines | ? |
| Best feature set | TF-IDF + BigFive | ? |
| Best held-out PCA3D R² | 0.361 | ? |
| Improvement over semantic baseline | +0.219 | ? |
| Primary explanatory framework | BigFive psychological traits | ? |
| PC1 predictability | Negative (UNPREDICTED) | ? |
| PC2 predictability | 0.732 | ? |
| PC3 predictability | 0.440 | ? |
| Gemma axis R² | 0.695 | ? |
| Best-explained cluster | procedural_professional | ? |
| Worst-explained cluster | other (developmental stages) | ? |
| Plateau trigger | Round 3 | ? |

---

## What Convergence Would Mean

If Codex/GPT-5.5 independently found:
- BigFive as the dominant explanatory framework → strong cross-model convergence
  on the psychological interpretation. Supports treating BigFive as a principled
  lens on activation geometry, not a model-specific artifact.
- Similar PC1 unpredictability → supports the interpretation that PC1 captures
  model-internal organization not visible from human-legible features.
- Same roles as best/worst explained → supports treating procedural-professional
  as the most "semantically transparent" activation cluster, and "other" as the
  most cryptic.

## What Divergence Would Mean

If Codex/GPT-5.5 found different explanatory dimensions or different best/worst roles:
- Systematic divergence would suggest that the latent dimensions are not stable
  across hypothesis-generation engines.
- Conceptually meaningful disagreement (e.g., Codex emphasizes domain-specificity
  while Claude emphasizes psychological traits) would be a finding about what
  each model considers the most salient axes of role variation.
- Random disagreement would undermine the interpretive value of either analysis.

---

## Methodological Notes and Limitations

1. **Target proxy**: The pseudo-PCA3D target is derived from Qwen cluster cosines,
   not from actual Qwen role-vector PCA. The cosines are activation-derived (7
   named cluster centroids), which means PC1 of this matrix may not correspond to
   PC1 of the full Qwen activation space.

2. **N=275**: Ridge regression with 5-fold CV on 275 observations is underspecified
   for high-dimensional feature sets. The TF-IDF SVD reduction to 50 components
   was necessary to avoid overfitting, but may lose relevant signal.

3. **BigFive profiles are literature-derived**: The BigFive trait assignments in
   `bigfive_profiles.json` were assigned by an LLM (likely Claude or GPT-4) during
   the original Paper 1 analysis, not from human rater studies. They may encode the
   assigning model's priors about role stereotypes, which could explain the strong
   BigFive predictability without requiring that the activation geometry is truly
   "psychological."

4. **Claude's hypothesized dimensions were not tested**: The plateau rule stopped
   the loop before reaching Claude's 10 binary dimensions. They may add signal on
   alternative target definitions or with smaller feature sets. A separate targeted
   test of these dimensions is warranted.

5. **No Codex comparison available**: This document cannot yet serve as a
   convergence test. It documents the Claude-side result for future comparison.
