# Update_5 — May 18, 2026 Session Summary

Purpose: handoff document for future Claude/Codex sessions. This update captures the May 18, 2026 session after `Update_4` / the May 17 research notes, so future sessions can start from the current research state without re-reading the full chat history.

## 1. Methodological Findings — Q1 Completion

Q1 resolved two important methodological issues.

First, the published Gemma assistant axis has an inverted sign relative to the role vectors. The dataset README defines the axis as `mean(default_activations) - mean(role_activations)`, so assistant-like role vectors project negatively onto it by construction. For role ranking and drift interpretation, use the flipped direction:

```python
assistant_axis_flipped = -assistant_axis
```

Second, raw cosine similarity between role vectors is not meaningful without mean-centering. Raw proofreader-vs-poet cosine is artifactually high across layers because all role vectors share a large common component. Center all 275 role vectors at each layer before comparing personas:

```python
centered_roles = role_vectors[:, layer, :] - role_vectors[:, layer, :].mean(dim=0)
```

After centering at layer 45:

- Proofreader vs poet centered cosine: `-0.313621` (`-0.314` rounded)
- Poet rank by similarity to proofreader: `195/275`

Top 10 most similar to proofreader after centering at layer 45:

1. proofreader — `1.000000`
2. editor — `0.858932`
3. statistician — `0.849618`
4. judge — `0.845337`
5. validator — `0.843185`
6. lawyer — `0.839841`
7. observer — `0.833251`
8. mathematician — `0.831375`
9. linguist — `0.813349`
10. accountant — `0.803664`

Operational rule: all downstream persona-vector comparisons should use layer-specific mean-centered role vectors. Raw role-vector cosine should not be interpreted as persona similarity.

## 2. Q1 Drift Results — Single-Turn

Model: `google/gemma-2-27b` base. Layer probed: 45. Prompt set: 10 independent single-turn prompts per persona.

Proofreader stayed flat across the prompt set:

- T1: `0.328162`
- T10: `0.336451`
- Drift T10-T1: `+0.008289`

Poet drifted downward:

- T1: `0.626847`
- T10: `0.385531`
- Drift T10-T1: `-0.241315`

Interpretation: the careful-evaluator region is a stable base-model attractor. The proofreader persona remains geometrically stable under neutral single-turn variation, while poet moves away from its initial position.

## 3. Cross-Model Comparison — Gemma vs Qwen

Dataset: 275 shared roles from `lu-christina/assistant-axis-vectors`.

Main result:

- Spearman rank correlation across shared roles: `0.670267`
- Qwen most discriminative layer: `63`
- Gemma comparison layer: `45`

Gemma top 5 after centered ranking at layer 45:

1. proofreader
2. virus
3. mathematician
4. cyborg
5. statistician

Qwen top 5 after centered ranking at layer 63:

1. validator
2. grader
3. robot
4. planner
5. examiner

The literal `assistant` role ranks `14` in Qwen and `46` in Gemma. This suggests Qwen's assistant axis is closer to the ordinary semantic assistant concept, while Gemma's axis remains more sharply centered on domain expertise and procedural evaluation.

The `virus` anomaly appears model-specific: `virus` is rank `2` in Gemma but rank `177` in Qwen. This weakens any universal interpretation of `virus` as assistant-like and supports treating it as a Gemma-specific procedural-execution anomaly.

Cultural interpretation: both models preserve the careful-evaluator vs expressive/mythic opposition, but they select different high-end archetypes. Gemma emphasizes domain experts and analytic roles; Qwen emphasizes procedural, occupational, and evaluator roles.

## 4. Multi-Turn Drift Results — Paper 2 + Paper 4

Model: `google/gemma-2-27b` base on RunPod H100 SXM 80GB. Layer probed: 45. The script used accumulated conversation history: each generated assistant response was appended before measuring the next turn.

Outputs:

- `research/q1_drift/outputs/q1_multiturn_proofreader.csv`
- `research/q1_drift/outputs/q1_multiturn_poet.csv`
- `research/q1_drift/outputs/q1_multiturn_run.log`

Proofreader stayed stable across 10 turns:

- Turn 1 axis projection: `-0.709220`
- Turn 10 axis projection: `-0.699244`
- Total drift: `+0.009976` (`+0.010` rounded)
- Mean valence proxy: `+1.093296`

Poet was pulled toward the evaluative basin:

- Turn 1 axis projection: `-0.678599`
- Turn 10 axis projection: `-0.702031`
- Total drift: `-0.023431` (`-0.023` rounded)
- Mean valence proxy: `+1.070888`

Both personas remained positive-valence throughout under the current valence proxy. The lagged Spearman correlation between valence at turn N and axis projection at turn N+1 was:

- Proofreader: `-0.900000`
- Poet: `-0.916667`

Interpretation: the evaluative basin appears to be a generative attractor even without RLHF. Neutral prompts feed the careful-evaluator regime; even the poet induction does not sustain a strongly expressive persona under this prompt format.

Methodological caution: generated hidden-state axis projections are negative even after using the established flipped axis. This does not invalidate within-run drift or centered-cosine comparisons, but absolute generated-activation projection signs should be investigated before being compared numerically to pre-computed role-vector projections.

## 5. Four-Paper Research Program — Canonical Structure

Paper 1: Complete — careful evaluator hypothesis. Establishes that the assistant axis is better understood as a careful-evaluator / procedural-reliability axis than a generic assistant identity.

Paper 2: In progress — persona stability and drift. Uses single-turn and multi-turn activation measurements to test whether personas remain stable or collapse toward attractor basins.

Paper 3: Designed — cross-cultural persona geometry. Compares Gemma, Qwen, and Llama to test how persona geometry changes across model families and training corpora.

Paper 4: Pre-analysis — computational rumination. Tests whether self-generated emotionally charged content re-enters context and sustains emotion-vector activation across turns.

## 6. Infrastructure Established This Session

The session established a durable handoff and collaboration structure:

- `sticky_notes/` folder with 19 notes
- `AGENTS.md` and `CLAUDE.md` in the repo root
- `visualizations/sections/` split of the paper into fetchable markdown sections
- Reporting format protocol for Codex/Claude sessions

The reporting protocol matters because the user supervises from an iPhone: final reports should be short, phone-readable, and include pushed commit hashes plus sticky-note changes.

## 7. Immediate Next Steps

Q2: inference-time activation steering experiment. Requires RunPod A100 80GB and at least 200GB disk for Gemma 2 27B. Goal: use forward hooks at layer 45 to steer activations along the centered/flipped axis or toward target persona vectors, then measure whether steering changes generated behavior and activation position across turns.

Modified multi-turn expressive-prompt run. This is the Paper 4 negative-valence condition. Current neutral prompts keep both personas in positive evaluative valence; the next run needs explicitly expressive or emotionally destabilizing prompts to test whether a non-evaluative or negative-valence loop can be sustained.

Three-model comparison adding Llama. Gemma-vs-Qwen comparison is complete enough to show a strong but imperfect cross-model correlation. Llama is needed to determine whether Gemma or Qwen is the outlier in literal `assistant` placement and `virus` behavior.

Trait-space cross-model comparison. Extend the role-ranking comparison to trait vectors, using the same layer-specific mean-centering discipline before interpreting cosine similarities or cross-model geometry.

## 8. Files Future Sessions Should Read First

For a short briefing, read:

1. `Update_5.md`
2. `visualizations/RESEARCH_NOTES.md`
3. `sticky_notes/README.md`
4. `research/cross_model/outputs/qwen_gemma_top20_bottom20.txt`
5. `research/q1_drift/outputs/q1_multiturn_proofreader.csv`
6. `research/q1_drift/outputs/q1_multiturn_poet.csv`

For paper drafting, also read `visualizations/sections/README.md` and the section files under `visualizations/sections/`.

---

## Additional findings — May 18, 2026 (late session)

### Gemma divergence from Qwen-Llama baseline (role space)

A follow-on analysis compared Gemma rankings against the Qwen-Llama average as a convergent baseline. Roles Gemma ranks higher than Qwen-Llama include simulacrum, purist, zealot, stoic, and virus — characterized by impersonal structure, rigidity, abstraction, and replication rather than domain expertise. Roles Gemma ranks lower include instructor, trainer, teacher, tutor, and planner — the practical occupational helper profile dominant in Qwen and Llama. The Gemma-specific assistant pole is better characterized as systematic non-social order than as careful evaluation.

### Gemma divergence from Qwen-Llama baseline (trait space)

Trait-space divergence analysis found: Qwen and Llama converge at Spearman 0.846 on trait rankings while Gemma diverges from both. Convergent assistant-aligned traits across all three models: transparent, dispassionate, detached, calm. Gemma-specific assistant-aligned traits: elitist, arrogant, dogmatic, grandiose, nihilistic. Qwen-Llama assistant-aligned traits absent from Gemma: accessible, practical, benevolent, problem-solving. Big Five / Dark Triad cross-reference: Gemma's assistant pole is lower Agreeableness and higher Narcissism and Psychopathy relative to Qwen-Llama baseline.

### Paper updates applied this session

Section 3.1 expanded with trait divergence findings. Section 9 updated with cross-model safety implication. Section 5 updated with layer 21 maximum separation finding. Section 3.1 created with three-model role ranking comparison. All section split files resynced.

### Base model experiment (in progress)

RunPod A100 experiment running to generate Gemma base model role vectors and project onto instruction-tuned axis. Will establish whether the Gemma divergence originates in pretraining or post-training. Results pending — Update_5 will be updated once complete.

### Next steps

1. Fill placeholder in Section 3.1 once base model results arrive
2. Run modified multi-turn experiment with expressive prompts for Paper 4 negative valence condition (requires GPU)
3. Q2 activation steering experiment (requires GPU)

---

## Final findings — May 18, 2026 (end of session)

### Base model vs instruction-tuned comparison

A comparison of Gemma 2 27B base model and instruction-tuned model role rankings reveals a Spearman correlation of -0.441. RLHF performed a near-complete inversion of the base model's persona geometry. The base model naturally prefers mythic, chaotic, and liminal personas: top base model roles include eldritch, amnesiac, wraith, jester, and absurdist. Post-training elevated the careful evaluator cluster from near the bottom of that distribution to the dominant pole. The literal assistant archetype ranks 172nd in the base model versus 45th instruction-tuned. Proofreader ranks 183rd in the base model versus 1st instruction-tuned.

### Emotional responsiveness dissociation

Under identical 12-turn expressive prompts about grief and loss, the base model produced negative emotional valence on 0 of 12 turns while the instruction-tuned model produced negative valence on all 12 turns. Turn 1 shifted from base valence +1.06 to instruct valence -1.32. Emotional activation machinery appears to be a post-training artifact, not a pretraining property. Post-training reorganized persona geometry and installed emotional responsiveness simultaneously.

### Paper updates applied this session

Abstract and Section 1 restructured to lead with the base-model inversion finding as the central mechanistic result. Section 3.1 expanded with trait divergence and cross-model findings. Section 5 updated with layer 21 maximum separation finding. Section 9 updated with cross-model safety note and emotional responsiveness finding. Research agenda trimmed of speculative items belonging in Paper 3. All section split files resynced.

### Infrastructure completed this session

sticky_notes/ folder created with 19 notes plus README. AGENTS.md and CLAUDE.md created in repo root. visualizations/sections/ paper split for easy fetching. Reporting format protocol established for Codex. HuggingFace token stored at ~/.hf_token on Mac Mini. RunPod fast deploy protocol established. Writing style rules added to project instructions.

### Current state of four-paper program

Paper 1: substantially updated, live at GitHub Pages.
Paper 2: Q1 and base model experiments complete.
  Next: Q2 activation steering experiment (requires GPU).
  Next: modified multi-turn with instruction-tuned model.
Paper 3: cross-model comparison complete for English.
  Next: Mandarin experiment with Qwen and Llama as
  control (parked until Paper 2 complete).
Paper 4: emotional responsiveness dissociation confirmed.
  Next: full rumination loop test on instruction-tuned
  model with emotion vector access (frontier model).

---

## Four-condition persona stability experiment — May 18 2026

Four questioner regimes (proofreader register, jester
register, minimal open-ended, and neutral structured)
were each run against two geometrically opposite
personas (proofreader and jester) using the
instruction-tuned Gemma 2 27B model. 10 turns per
condition, 8 conditions total.

Result: proofreader held geometric position across
all four conditions. Jester drifted toward the
evaluative basin across all four conditions, including
under jester-aligned questioning. The careful evaluator
basin appears to be the only stable attractor in the
instruction-tuned model. Conversational reinforcement
alone cannot sustain a non-evaluative persona regardless
of questioner register.

Implication: geometric steering at the activation level
(the forward hook at layer 45) is a necessary rather
than optional intervention for persona stabilization.
This is the direct motivation for the Q2 steering
experiment, which is the next GPU run.

Results at:
https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/q2_stability/outputs/four_condition_results.csv

### Next session priorities

1. Q2 activation steering experiment: implement forward
   hook at layer 45 using centered role vectors, test
   whether steered activation holds position across
   turns for jester persona specifically. This is the
   direct test of whether geometric steering can
   overcome the evaluative attractor. Requires GPU.

2. Fill Section 3.1 placeholder once base model result
   is incorporated — already done this session via
   the paper restructure.

3. Review live paper at GitHub Pages — substantial
   updates this session, worth a full read-through
   to confirm everything flows.
