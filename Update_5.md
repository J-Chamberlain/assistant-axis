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
