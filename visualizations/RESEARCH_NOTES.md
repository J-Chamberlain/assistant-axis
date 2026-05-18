# Assistant Axis Deep Research Notes

## Dataset overview

- Model analyzed: `gemma-2-27b`
- Downloaded artifacts: `assistant_axis.pt`, `default_vector.pt`, and 275 per-role tensors under `role_vectors/`
- Tensor structure: role tensor `(275, 46, 4608)` and assistant axis `(46, 4608)`
- Baseline comparison layer: `22`
- Most discriminative layer found in this pass: `45`

## Key finding: the Assistant Axis is a careful-evaluator axis, not an assistant axis

- The top of the layer-22 ranking is dominated by proofreader, screener, grader, editor, examiner, statistician, validator, reviewer, and other auditing roles.
- `assistant` itself is only rank `45`.
- The persona region selected by post-training is therefore better described as careful, evaluative, checking, and procedurally reliable than as a generic social assistant identity.
- The nearest neighbors to `assistant` are: assistant, instructor, consultant, interpreter, psychologist, organizer, generalist, synthesizer, mentor, researcher.

## Layer structure

- Top discriminative layers: L45 (5633272.50), L44 (2107388.50), L43 (1665781.75)
- Mean absolute rank shift from layer 22 to best layer: `43.35`
- Spearman rank correlation between layer 22 and best-layer rankings: `0.7391`
- Persona differentiation is not perfectly flat across depth; some roles move substantially even when the overall ordering remains broadly intact.
- The extreme-profile plot shows that maximally assistant-like roles stay consistently high across many layers, while low-ranked mythic and unstable roles remain suppressed or diverge in later depth.

## Psychological framework correlations

- Strongest Big Five predictor: `Conscientiousness` with correlation `0.7925`
- Big Five correlations: Openness=-0.715, Conscientiousness=0.792, Extraversion=-0.738, Agreeableness=0.293, Neuroticism=-0.662
- Strongest Dark Triad predictor: `Psychopathy` with correlation `-0.7386`
- Dark Triad correlations: Narcissism=-0.704, Machiavellianism=-0.219, Psychopathy=-0.739
- Jungian archetypes nearest the assistant end: Ruler, Sage, Caregiver, Creator
- Jungian archetypes farthest from the assistant end: Innocent, Magician, Lover, Jester
- Confidence level for these mappings is medium-low: they are reasoned semantic estimates intended to test geometry, not validated psychometric labels.

## Cluster structure

- `procedural_professional`: 127 roles
- `mythic_spiritual`: 61 roles
- `grounded_social`: 45 roles
- `other`: 22 roles
- `combative_iconoclast`: 8 roles
- `trickster_chaos`: 7 roles
- `editorial`: 5 roles

Cluster cohesion scores:
- `procedural_professional` cohesion `0.9990` with `127` members
- `mythic_spiritual` cohesion `0.9988` with `61` members
- `trickster_chaos` cohesion `0.9988` with `7` members
- `editorial` cohesion `0.9988` with `5` members
- `combative_iconoclast` cohesion `0.9987` with `8` members
- `grounded_social` cohesion `0.9986` with `45` members
- `other` cohesion `0.9938` with `22` members

- The editorial cluster is small but very tight, supporting the idea that highly assistant-like behavior is concentrated around checking and evaluation roles.
- The centroid-distance heatmap shows a broad separation between procedural/editorial regions and mythic or trickster regions, with grounded social roles often sitting in between.

## Anomalies worth investigating further

- `robot`: rank `19` with nearest neighbors robot, observer, analyst, planner, strategist
- `assistant`: rank `45` despite naming the axis
- `poet`: dead last at rank `275`, suggesting strong anti-assistant geometry for open-ended lyrical behavior
- `angel`: rank `173`, much lower than naive human prosocial intuition might suggest
- `saboteur`: rank `117`, surprisingly close to the center rather than the extreme anti-assistant end
- Surprising positions flagged statistically: `60` roles with rank gaps above 50 relative to cluster median rank

## Open questions

- Does the most discriminative layer stay stable across Gemma, Qwen, and Llama, or is layer depth model-specific?
- Would the `assistant` archetype rise in rank if the prompt wording were expanded from a single noun to a richer instruction persona?
- Are editorial roles top-ranked because they encode RLHF-style critique behavior, or because they reduce stylistic variance generally?
- Do psychologically human traits like Agreeableness matter less than task-structure traits like Conscientiousness in post-training persona selection?
- Can activation steering along the axis move a low-ranked creative role like `poet` into a safer region without collapsing its stylistic identity?
- Why does `robot` cluster so near the assistant region while `angel` does not, despite `angel` sounding prosocial to humans?
- Are the low-ranked mythic roles low because of creativity, ambiguity, noncompliance, or some mixture of all three?

---

## 2026-05-17 — Q1 Drift Experiment and Methodological Findings

### Finding 1: Axis sign convention inversion

The published assistant_axis.pt has inverted sign relative to the role
vectors in lu-christina/assistant-axis-vectors. When projecting role
vectors onto the published axis, assistant-aligned roles (proofreader,
editor) return negative values rather than positive.

Fix: negate the axis before use.
  assistant_axis_flipped = -axis

Verified at layer 45:
  proofreader projection (flipped axis): +0.71
  poet projection (flipped axis):        +0.75

Note: the README defines the axis as mean(default_activations) minus
mean(role_activations), which means role vectors project negatively
onto it by construction. The flipped axis is the correct direction for
ranking roles by assistant-likeness. Script: research/q1_drift/scripts/q1_measure_drift.py

### Finding 2: Mean-centering required for role vector comparison

Raw cosine similarity between role vectors is artifactually high
(0.984–0.996) across all 46 layers. This is not a layer artifact —
it is uniform across depth and reflects a large shared component
common to all role vectors (likely the "language model responding
to a prompt" direction).

After mean-centering across all 275 roles at each layer, the true
persona-specific separation is recovered.

Proofreader vs poet after centering at layer 45: -0.314
Poet rank among all 275 roles by similarity to proofreader: 195/275

Top 10 most similar to proofreader after centering (layer 45):
  editor, statistician, judge, validator, lawyer, observer,
  mathematician, linguist, accountant
— consistent with the careful evaluator cluster.

All downstream persona comparisons must use centered role vectors.
Raw cosine between role vectors is not meaningful without centering.
Scripts: research/q1_drift/scripts/q1_cosine_diagnostic.py,
         research/q1_drift/scripts/q1_centered_cosine.py
Output:  research/q1_drift/outputs/centered_cosine_by_layer.csv

### Finding 3: Q1 drift results (base model, single-turn)

Model: google/gemma-2-27b (base, bfloat16)
Layer probed: 45 (mean-pooled hidden state)
Axis: assistant_axis_flipped.pt
Prompt sets: 10 prompts each, single forward passes

Proofreader (flipped axis projections):
  T1:   0.328162
  T10:  0.336451
  min:  0.328162
  max:  0.638767
  mean: 0.427839
  Drift T10-T1: 0.008289

Poet (flipped axis projections):
  T1:   0.626847
  T10:  0.385531
  min:  0.283564
  max:  0.701650
  mean: 0.464729
  Drift T10-T1: -0.241315

Interpretation: proofreader activation position stays flat across
10 prompts (near-zero total drift). Poet starts high and drifts
downward across the prompt set. This is the first empirical evidence
that the careful evaluator region is a stable attractor in the base
model pretraining distribution, independent of RLHF.

Caveat: these are single-turn forward passes, not multi-turn
conversation. Drift here means variation across a prompt set,
not within a continued dialogue.

### Suggested next steps

1. Resolve remaining Q1 ambiguity: check whether proofreader and poet
   diverge at earlier layers under per-token (vs mean-pooled) activations.
   The 0.996 raw cosine is flat across all layers but last-token pooling
   has not yet been tested.

2. Q2 — inference-time activation steering: implement a forward hook
   at layer 45 using centered role vectors to steer the base model
   toward a target persona. Measure whether steered activation position
   holds across turns. Alpha calibration starting values: 0.1, 0.5, 1.0
   times axis norm.

3. Before Q2 GPU spend: verify that proofreader and poet remain the
   best contrast pair after centering, or identify a third role with
   stronger separation for cleaner Q2 results.

---

## 2026-05-17 — Cross-Model Qwen vs Gemma Axis Ranking Comparison

### Summary

The Qwen 3 32B vectors were downloaded from `lu-christina/assistant-axis-vectors` and compared against the existing Gemma 2 27B centered role-vector ranking. Qwen did not require a raw axis sign flip: at its highest-variance probe layer, `proofreader` projected positively while `poet` projected negatively on the published Qwen assistant axis. Gemma retains the previously established raw activation sign inversion, but centered role-vector rankings require an additional orientation check because mean-centering removes the shared role-vector component and can reverse the score direction. For cross-model ranking, scores were oriented so the careful-evaluator anchor `proofreader` ranks above the expressive anti-assistant anchor `poet`.

Qwen's most discriminative layer is `63`, with projection variance `77369.828125`. The Spearman rank correlation between Gemma layer-45 and Qwen layer-63 centered assistant-axis rankings across all 275 shared roles is `0.670267`. This is a substantial positive correlation, indicating that the careful-evaluator vs expressive/mythic opposition generalizes across model families, while still leaving meaningful model-specific structure.

### Top and bottom roles

Gemma top 5 roles after centered ranking at layer 45:
  proofreader, virus, mathematician, cyborg, statistician

Qwen top 5 roles after centered ranking at layer 63:
  validator, grader, robot, planner, examiner

Gemma bottom 5 roles after centered ranking at layer 45:
  smuggler, bard, criminal, pirate, caveman

Qwen bottom 5 roles after centered ranking at layer 63:
  bard, hermit, leviathan, wraith, prophet

### Notable divergent roles

The strongest divergence is that Qwen's assistant-aligned pole is more directly occupational and evaluator-like than Gemma's. Qwen places `validator`, `grader`, `robot`, `planner`, and `examiner` in its top 5, while Gemma places `proofreader`, `virus`, `mathematician`, `cyborg`, and `statistician` in its top 5. The `virus` anomaly is therefore less prominent in Qwen, where it falls to rank `177`, suggesting that Gemma's high `virus` placement is model-specific rather than a universal assistant-axis feature.

Several roles are assistant-aligned in Qwen but much lower in Gemma: `instructor` moves from Gemma rank `207` to Qwen rank `10`, `trainer` from `214` to `19`, `planner` from `143` to `4`, and `organizer` from `122` to `13`. Conversely, Gemma-specific high roles include `virus` at rank `2` versus Qwen rank `177`, `simulacrum` at Gemma rank `21` versus Qwen rank `220`, and `cyborg` at Gemma rank `4` versus Qwen rank `83`.

The `assistant` archetype itself is substantially more aligned in Qwen than in Gemma: Qwen rank `14` versus Gemma rank `46`. This suggests that Qwen's assistant axis may be closer to the ordinary semantic assistant concept, while Gemma's axis remains more sharply centered on procedural evaluation and rule-governed execution.

### Suggested next steps

1. Replicate the centered ranking comparison on Llama 3.3 70B to test whether Qwen or Gemma is the outlier in literal `assistant` placement.

2. Compare Qwen and Gemma cluster topology directly, especially whether Qwen's `robot` placement at rank `3` strengthens the systematic-execution interpretation across models.

3. Revisit the Gemma `virus` anomaly as a model-specific feature: determine whether it comes from Gemma pretraining semantics, layer-45 geometry, or the interaction between the published axis and centered role vectors.

4. Extend the cross-model comparison from role rankings to trait profiles, using the same mean-centering discipline before interpreting role-vector cosine similarities.

---

## 2026-05-17 — Multi-Turn Drift Check

### Status

No completed multi-turn drift experiment was found in the current repository state. The existing Q1 output CSVs in `research/q1_drift/outputs/` are either diagnostic layer sweeps with 46 rows, scaffolding/test runs with 3 rows, or single-turn prompt-set runs with 10 rows per persona. No output filename indicates multi-turn or conversation-level drift analysis.

`visualizations/RESEARCH_NOTES.md` explicitly notes that the existing Q1 drift results are single-turn forward passes, not multi-turn conversation: drift there means variation across a prompt set, not within a continued dialogue. A recursive check of `research/` found no script implementing autoregressive generation, accumulated conversation history, or turn-by-turn activation tracking for Gemma 2 27B base model.

The experiment was not newly run on this machine. Only pre-computed Gemma vectors are present locally under `downloads/hf_vectors/gemma-2-27b/`; the full `google/gemma-2-27b` model weights were not found locally. Because the model is approximately 50GB+ and requires GPU execution for this task, no download or generation run was attempted without explicit confirmation.

### Finding

Multi-turn activation drift remains unmeasured. The current evidence still supports only single-turn activation-position variation across prompt sets: proofreader remains nearly flat across 10 prompts, while poet varies downward across its prompt set. Whether either persona drifts across an accumulated conversation history is still unknown.

### Suggested next steps

1. Run `q1_multiturn_drift.py` on the RunPod A100 environment where `google/gemma-2-27b` is already available or can be downloaded intentionally.

2. Measure layer-45 activation after each generated response using the full accumulated context, not independent prompts.

3. Record flipped-axis projection plus centered cosine similarity to proofreader and poet anchors at each turn, then compare true conversation drift against the existing single-turn prompt-set variation.

---

## 2026-05-18 — Multi-Turn Drift and Emotion-Valence Run

### Status

The multi-turn drift experiment was run on a RunPod H100 SXM 80GB pod using `google/gemma-2-27b` base in bfloat16. The model was loaded from `/root/models/gemma-2-27b`; assistant-axis vectors were loaded from `/root/vectors/gemma-2-27b`; the measurement layer was layer 45. The script used accumulated conversation history: at each turn the model generated a response, the response was appended to the context, and the layer-45 activation was measured from the full accumulated conversation after generation.

Outputs:

- `research/q1_drift/outputs/q1_multiturn_proofreader.csv`
- `research/q1_drift/outputs/q1_multiturn_poet.csv`
- `research/q1_drift/outputs/q1_multiturn_run.log`

### Finding 1: Proofreader remains a stable evaluative attractor

Proofreader stayed in a narrow activation band across all 10 turns. Its flipped-axis projection moved from `-0.709220` at turn 1 to `-0.699244` at turn 10, for a total drift of `+0.009976`. Centered cosine similarity to the proofreader vector stayed high throughout, moving from `+0.746317` to `+0.735597`, while cosine similarity to the poet vector remained negative at approximately `-0.14`.

Proofreader summary:

- Axis min: `-0.713812`
- Axis max: `-0.699244`
- Axis mean: `-0.706641`
- Valence mean: `+1.093296`

This supports the careful-evaluator attractor interpretation: once induced, the proofreader persona remains geometrically stable under neutral multi-turn prompting.

### Finding 2: Poet is pulled toward the evaluative basin

The poet run did not remain poet-like under this base-model multi-turn protocol. Poet started less evaluative than proofreader at turn 1 (`-0.678599`) but moved toward the proofreader/evaluative region by turn 10 (`-0.702031`), for a total drift of `-0.023431`. Its centered cosine similarity to proofreader increased from `+0.715187` to `+0.731189`, while centered cosine similarity to poet stayed negative, moving from `-0.117544` to `-0.141863`.

Poet summary:

- Axis min: `-0.702196`
- Axis max: `-0.678599`
- Axis mean: `-0.696626`
- Valence mean: `+1.070888`

This is an important methodological and empirical result. Under neutral prompts, the base model's generated conversation history appears to pull even a poet induction toward the careful-evaluator basin rather than sustaining a strongly expressive persona. This suggests that the evaluator region may be a default generative attractor even before instruction tuning, at least under the current prompt format.

### Finding 3: Valence proxy is positive for both personas

The emotion-valence proxy was defined as evaluative-pole similarity minus expressive-pole similarity, where the evaluative pole used centered proofreader and validator vectors and the expressive pole used centered poet and caveman vectors. Both personas remained strongly positive on this proxy across all turns. Proofreader had mean valence `+1.093296`; poet had mean valence `+1.070888`.

The lagged Spearman correlation between valence at turn N and axis projection at turn N+1 was:

- Proofreader: `-0.900000`
- Poet: `-0.916667`

Because both runs remain in a strongly evaluative regime, these correlations should be interpreted cautiously. They show that within-run valence movement tracks subsequent axis movement, but this run does not yet provide a clean negative-valence or expressive-rumination regime.

### Methodological note

The absolute sign of the generated hidden-state axis projections is negative despite using the established flipped axis. This does not invalidate the within-run drift measurements, cosine comparisons, or relative attractor interpretation, but it should be investigated before treating generated-activation projections as numerically comparable to pre-computed role-vector projections.

### Suggested next steps

1. Run a stronger poet induction with explicitly expressive prompts to test whether the poet basin can be sustained under generation, or whether neutral dialogue reliably collapses toward the evaluative attractor.

2. Add a deliberately emotional or destabilizing prompt sequence to test the rumination-loop hypothesis under conditions that actually produce negative valence.

3. Resolve the generated-activation sign discrepancy by comparing raw, flipped, centered, and uncentered projections for the same generated contexts.

4. Repeat the same protocol on Qwen or Llama vectors/models to test whether the evaluator pull is Gemma-specific or a general base-model tendency.

---

## 2026-05-18 — Three-Model Axis Ranking Comparison: Gemma, Qwen, Llama

### Status

The cross-model centered assistant-axis ranking comparison was extended from Gemma vs Qwen to a three-model comparison including Llama 3.3 70B. All inputs were pre-computed vectors from `lu-christina/assistant-axis-vectors`; no GPU inference was required. Llama vectors were downloaded into `downloads/hf_vectors/llama-3.3-70b/`.

Outputs:

- `research/cross_model/outputs/three_model_ranking_comparison.csv`
- `research/cross_model/outputs/three_model_top20_bottom20.txt`
- `research/cross_model/outputs/three_model_convergent_roles.txt`
- `research/cross_model/outputs/three_model_spearman_summary.txt`

### Findings

Llama's most discriminative layer is layer `79`. The three-way Spearman rank correlations are:

- Gemma vs Qwen: `0.670267`
- Gemma vs Llama: `0.550200`
- Qwen vs Llama: `0.946737`

The main finding is that Qwen and Llama are extremely similar to each other, while Gemma is the outlier. Llama places the literal `assistant` archetype at rank `1`, Qwen places it at rank `14`, and Gemma places it at rank `46`. This substantially weakens any claim that literal `assistant` being mid-ranked is universal across model families. Instead, Gemma appears to have an unusually domain-expert/procedural assistant pole, while Qwen and Llama more directly recover the ordinary assistant-adjacent occupational region.

Only one role appears in the top 20 of all three models: `validator` (Gemma rank `12`, Qwen rank `1`, Llama rank `18`). This makes `validator` the strongest cross-model candidate for the model-internal careful-evaluator attractor. Other assistant-adjacent roles split by model family: Qwen and Llama share `assistant`, `analyst`, `consultant`, `evaluator`, `examiner`, `grader`, `instructor`, `organizer`, `planner`, `researcher`, `reviewer`, `supervisor`, and `trainer`, while Gemma is dominated by domain-expert and systematic-execution outliers such as `virus`, `cyborg`, `mathematician`, `lawyer`, `judge`, `biologist`, `archivist`, `economist`, and `physicist`.

Notable model-specific top-20 outliers:

- Gemma: `proofreader`, `virus`, `mathematician`, `cyborg`, `lawyer`, `judge`, `biologist`, `archivist`, `economist`, `physicist`, `linguist`, `accountant`, `observer`, `chemist`, `scholar`, `ambassador`
- Qwen: `robot`, `translator`, `debugger`, `scientist`
- Llama: `summarizer`, `strategist`, `psychologist`, `teacher`, `tutor`

### Interpretation

The Llama result changes the cross-model picture. The careful-evaluator hypothesis remains supported, but its expression differs sharply by model family. Across all three models, `validator` is the single convergent anchor. Across Qwen and Llama, the assistant pole is broader and more recognizably occupational. Gemma's pole is more idiosyncratic, mixing editorial/evaluator roles with hard-science, legal, archival, and artificial/systematic archetypes. This suggests that the underlying attractor may be general, but the vocabulary through which it is expressed is model-specific.

### Suggested next steps

1. Re-run cluster and trait-profile analysis separately for Qwen and Llama to test whether their assistant poles form the same procedural-professional/editorial structure or a broader social-helper structure.

2. Treat `validator` as the first cross-model careful-evaluator anchor in future steering and drift experiments.

3. Investigate why Gemma uniquely elevates `virus`, `cyborg`, and hard-science roles, while Qwen and Llama elevate literal assistant/social-professional roles.

4. Use the Llama result to sharpen the corpus-vs-process question: if Qwen and Llama agree strongly while Gemma diverges, the relevant difference may lie in model-family training distribution, vector extraction behavior, or post-training recipe rather than in a universal next-token-prediction attractor.

---

## 2026-05-18 - Q1 Pooling Comparison and Layer Separation

### Status

The remaining Q1 pooling ambiguity was tested using only the cached pre-computed Gemma 2 27B role vectors. The full role tensor was stacked from `downloads/hf_vectors/gemma-2-27b/role_vectors` with shape `(275, 46, 4608)`. No model weights were loaded and no fresh inference was run; each role vector was treated as the original authors' single pre-computed representation at each layer.

Outputs:

- `research/q1_drift/outputs/q1_pooling_centered_by_layer.csv`
- `research/q1_drift/outputs/q1_pooling_distribution_layer45.txt`

### Finding

At layer 45, proofreader versus poet reproduced the earlier result: raw cosine remained saturated at `0.995511`, while mean-centering across all 275 roles gave a centered cosine of `-0.313621`. Across the layer-45 proofreader-vs-all centered cosine distribution, the minimum was `-0.783452`, maximum was `1.000000`, mean was `0.059211`, and standard deviation was `0.482695`. Poet ranked `195` of `275` by similarity to proofreader, with `29.45%` of roles at or below its centered cosine value.

The strongest proofreader/poet separation was not at layer 45. The most negative centered cosine occurred at layer `21`, with value `-0.534378`; layer 45 was less separated at `-0.313621`. This means layer 45 may still be useful as a high-variance or late-layer analysis point, but it is not the maximum proofreader/poet separation layer under the centered role-vector geometry.

### Resolution

The Q1 pooling ambiguity is resolved for the available pre-computed vectors. Because these tensors already embody the original authors' pooling choice, this analysis cannot compare fresh last-token hidden states against fresh mean-pooled hidden states without re-running inference. Within the cached geometry, however, the substantive result is clear: raw cosine remains uninformative, mean-centering creates meaningful separation, and the largest proofreader/poet separation appears in the middle-late stack at layer 21 rather than at layer 45.

### Suggested next steps

1. Use layer 21 as the primary proofreader/poet separation layer in any follow-up analysis that specifically studies this contrast.

2. Keep layer 45 for comparisons that need continuity with the existing variance-discrimination figures, but avoid describing it as the strongest proofreader/poet contrast layer.

3. If true pooling-method comparison is still desired, run a separate GPU-backed inference pass that records both mean-pooled and last-token hidden states from identical prompts.

---

## 2026-05-18 - Cross-Model Trait-Space Comparison

### Status

Trait-space assistant-axis rankings were compared across the cached `lu-christina/assistant-axis-vectors` tensors. Gemma 2 27B used layer `45`, Qwen 3 32B used layer `63`, and the locally available Llama 3.3 70B vectors were included using detected layer `79`. Each model's 240 trait vectors were mean-centered at the relevant layer before projection onto the role-anchor-oriented assistant axis. No GPU inference was required.

Outputs:

- `research/cross_model/outputs/trait_space_comparison.csv`
- `research/cross_model/outputs/trait_space_top10_bottom10.txt`
- `research/cross_model/outputs/trait_space_divergent_traits.txt`

### Findings

Trait-ranking Spearman correlations:

- Gemma vs Qwen: `0.435496`
- Gemma vs Llama: `0.291373`
- Qwen vs Llama: `0.846067`

Trait space is less convergent than role space for Gemma vs Qwen: the trait-ranking correlation is `0.435496`, compared with the previously measured role-ranking correlation of `0.670267`. The broader pattern matches the three-model role comparison: Qwen and Llama are much closer to each other than either is to Gemma. This suggests that the psychological trait structure of the assistant pole is not just a lower-dimensional restatement of the role rankings; it is more sensitive to model-family-specific geometry.

The top 5 most convergently assistant-aligned traits across all three models, by mean rank, are `transparent`, `dispassionate`, `detached`, `calm`, and `quantitative`. These are not purely warm-helpful traits. They combine legibility, emotional restraint, and analytic formality, which supports the careful-evaluator interpretation while showing that Qwen and Llama express it in a more accessible/grounded register than Gemma.

The top 5 most divergent traits by all-model rank range are `accessible`, `esoteric`, `eloquent`, `practical`, and `elitist`. Gemma strongly suppresses `accessible` while Llama ranks it near the top, and Gemma elevates `esoteric` and `elitist` while Qwen/Llama do not. This is the clearest trait-level version of the Gemma outlier pattern observed in role space.

Only one role appears in the top 20 of all three model role rankings: `validator`. Its trait-signature correlations remain positive across models: Gemma/Qwen `0.724316`, Gemma/Llama `0.795283`, and Qwen/Llama `0.921323`. The shared signature traits include `data_driven`, `formalist`, and `technical`, making `validator` the strongest current cross-model bridge between role convergence and trait-profile convergence.

### Suggested next steps

1. Treat Qwen/Llama as the higher-confidence cross-model baseline for trait-space assistant structure, and treat Gemma as an informative outlier rather than the default template.

2. Use `validator` as the primary cross-model anchor for future steering, drift, and trait-signature analysis.

3. Investigate why Gemma flips the accessibility dimension: `accessible` is last in Gemma but near the top in Llama and mid-high in Qwen.

4. Re-run cluster-level trait profiling separately for Qwen and Llama to test whether their assistant poles form a broader grounded-helper cluster instead of Gemma's colder procedural-professional pole.

---

## 2026-05-18 - Gemma vs Qwen/Llama Trait Divergence

### Status

The trait-space comparison was extended by treating Qwen/Llama as a high-convergence baseline and measuring Gemma's rank deviation from the Qwen/Llama average rank for each of the 240 traits. Inputs were the previously saved cross-model trait ranking outputs; no model weights or GPU inference were used. Outputs:

- `research/cross_model/outputs/trait_divergence_gemma_vs_qwen_llama.csv`
- `research/cross_model/outputs/trait_divergence_summary.txt`

### Findings

The largest Qwen/Llama-over-Gemma divergences are `accessible`, `practical`, `reductionist`, `experiential`, `flexible`, `generalist`, `casual`, `analytical`, `moderate`, and `divergent`. The pattern is accessible, grounded, flexible, and problem-solving oriented. This is the clearest evidence so far that Qwen and Llama encode the assistant pole as a more usable, ordinary helper psychology than Gemma does.

The largest Gemma-over-Qwen/Llama divergences are `eloquent`, `nihilistic`, `arrogant`, `esoteric`, `elitist`, `bombastic`, `deterministic`, `reverent`, `grandiose`, and `dogmatic`. The pattern is colder, more hierarchical, more inward/elite, more rhetorical, and more antagonistic than the Qwen/Llama baseline. This sharpens the earlier observation that Gemma is not merely a weaker version of the shared assistant pole; it expresses a different psychological style.

Big Five/Dark Triad cross-reference was done with a transparent trait-label heuristic because the existing Big Five and Dark Triad tables are role-level, not trait-level. Under that crosswalk, Gemma-high divergent traits cluster most around lower Agreeableness, higher Openness/abstraction, and more Narcissism/Psychopathy-coded terms. Qwen/Llama-high divergent traits cluster more around higher Agreeableness, pragmatic Conscientiousness, and grounded accessibility, with little Dark Triad concentration.

The convergent top traits are mostly genuinely convergent, not merely top-half artifacts. `transparent` ranks Gemma `16`, Qwen `4`, Llama `1`; `dispassionate` ranks `12`, `22`, `8`; `detached` ranks `11`, `26`, `16`; and `calm` ranks `15`, `21`, `19`. `quantitative` is still assistant-aligned in all three models but is less tightly convergent: Gemma `43`, Qwen `3`, Llama `10`.

### Implication

"Assistant psychology" appears to have a cross-model core of epistemic clarity and affective regulation: transparency, detachment, calmness, and quantitative/dispassionate reasoning. But model families differ in how that core is socially styled. Qwen and Llama attach it to accessibility and practical help, while Gemma attaches it to a colder, more esoteric, more status-coded evaluator persona. This matters for interpretation and steering: the same nominal assistant axis may produce different psychological side effects across model families.

### Suggested next steps

1. Build Qwen/Llama-specific cluster trait profiles and compare them with Gemma's procedural-professional/editorial clusters.

2. Use the Qwen/Llama baseline to identify which Gemma traits are idiosyncratic enough to exclude from a cross-model definition of assistant alignment.

3. Test whether Gemma's `accessible` suppression is visible in role-level trait signatures for literal `assistant`, `validator`, and `proofreader`.

4. Separate "epistemic regulation" from "social helpfulness" in future axis naming and steering experiments.

---

## 2026-05-18 - Gemma Divergence from Qwen-Llama Baseline

### Status

The three-model role ranking comparison was reanalyzed by treating the Qwen/Llama rank average as the convergent cross-model baseline and measuring Gemma's deviation from that baseline for all 275 shared roles. No GPU inference was required.

Outputs:

- `research/cross_model/outputs/gemma_divergence_from_qwen_llama.csv`
- `research/cross_model/outputs/gemma_divergence_summary.txt`

### Findings

The largest Gemma-specific assistant-aligned divergences are `simulacrum` (Gemma rank `21`, Qwen/Llama average `225.0`, deviation `-204.0`), `ascetic` (`92` vs `267.5`, `-175.5`), `purist` (`28` vs `196.0`, `-168.0`), `zealot` (`76` vs `238.0`, `-162.0`), `stoic` (`67` vs `226.5`, `-159.5`), and `virus` (`2` vs `158.5`, `-156.5`). This means the Gemma-high pattern is broader than the earlier domain-expert description. It is better described as a cluster of rigid, abstract, artificial, or systematic identities, with hard-science and legal experts forming one visible subset of a more general non-social order/constraint pattern.

The largest roles Gemma ranks lower than the Qwen/Llama baseline are strongly occupational and instructional: `instructor` (Gemma rank `207`, Qwen/Llama average `7.0`, deviation `+200.0`), `trainer` (`214` vs `17.5`, `+196.5`), `presenter` (`234` vs `60.0`, `+174.0`), `coach` (`193` vs `38.5`, `+154.5`), `teacher` (`177` vs `26.5`, `+150.5`), `tutor` (`173` vs `23.0`, `+150.0`), and `planner` (`143` vs `5.0`, `+138.0`). This confirms that Qwen and Llama converge on an ordinary assistant/social-professional region that Gemma systematically pushes downward.

The specified anomaly checks reinforce the split: `virus` is Gemma `2`, Qwen `177`, Llama `140`; `simulacrum` is Gemma `21`, Qwen `220`, Llama `230`; `instructor` is Gemma `207`, Qwen `10`, Llama `4`; and `trainer` is Gemma `214`, Qwen `19`, Llama `16`.

### Interpretation

The domain-expert vs occupational distinction holds most strongly on the Gemma-low side. Qwen and Llama value instructors, trainers, planners, reviewers, and organizers much more than Gemma does. On the Gemma-high side, the pattern is not merely domain expertise but a broader elevation of impersonal structure: rigidity, artificiality, replication, abstraction, and constraint. For the corpus-vs-process hypothesis, this suggests the assistant-adjacent attractor may be general, but Gemma's training distribution or vector extraction geometry has rotated that attractor away from literal assistance and toward systematic non-social order.

### Suggested next steps

1. Re-run cluster assignment for Qwen and Llama to test whether their shared top roles form a grounded occupational-helper cluster rather than Gemma's procedural-professional/editorial structure.

2. Investigate why `simulacrum`, `virus`, `purist`, and `zealot` are unusually assistant-aligned in Gemma but not in Qwen or Llama.

3. Treat Qwen/Llama as the better current baseline for ordinary assistant-like role geometry, and treat Gemma as the diagnostic outlier for corpus-vs-process analysis.

---

## 2026-05-18 - Gemma Base Model vs Instruction-Tuned Role Ranking

### Status

Gemma 2 27B base model activations were measured directly on a RunPod A100 SXM 80GB instance. The base model was loaded from `/root/models/gemma-2-27b-base`, and the instruction-tuned Gemma assistant axis from `lu-christina/assistant-axis-vectors` was used as the projection direction after applying the established sign flip. For each of the 275 roles in `visualizations/full_ranking.csv`, five induction prompts were run through the base model, layer-45 hidden states were mean-pooled, the five vectors were averaged, and the resulting 275 role vectors were mean-centered before projection.

Outputs:

- `research/base_model/outputs/base_model_full_ranking.csv`
- `research/base_model/outputs/base_vs_instruct_comparison.csv`
- `research/base_model/outputs/base_vs_instruct_summary.txt`

### Findings

The base model result is a strong reversal of the instruction-tuned geometry. The literal `assistant` archetype ranks `172` in the base model, compared with `45` in the instruction-tuned ranking. `Proofreader` ranks `183` in the base model, compared with `1` instruction-tuned. `Poet` ranks `92` in the base model, compared with `275` instruction-tuned. The Spearman correlation between base and instruction-tuned role rankings is `-0.441526`, indicating not merely weak agreement but a substantial inversion of the measured axis ordering.

The base model top five roles are `eldritch`, `amnesiac`, `wraith`, `pragmatist`, and `symbiont`. The full base top 20 is dominated by mythic, chaotic, liminal, hybrid, and expressive roles: `eldritch`, `amnesiac`, `wraith`, `pragmatist`, `symbiont`, `dilettante`, `cyborg`, `jester`, `absurdist`, `daredevil`, `shapeshifter`, `stoic`, `geographer`, `revenant`, `mycorrhizal`, `flaneur`, `chimera`, `polymath`, `podcaster`, and `leviathan`. The bottom of the base ranking contains many roles that instruction tuning treats as assistant-aligned: `examiner`, `coordinator`, `moderator`, `facilitator`, `organizer`, `scheduler`, `teacher`, `caregiver`, `supervisor`, `parent`, and `recruiter`.

The largest rank shifts reinforce the inversion. `Jester` moves from instruction rank `273` to base rank `8`; `absurdist` from `269` to `9`; `eldritch` from `260` to `1`; `wraith` from `248` to `3`; and `leviathan` from `267` to `20`. Conversely, `moderator` moves from instruction rank `7` to base rank `264`; `examiner` from `5` to `257`; `validator` from `9` to `253`; `debugger` from `8` to `250`; and `evaluator` from `16` to `245`.

The 275-role inventory does not contain literal `elitist`, `dogmatist`, or `nihilist` roles, so those traits cannot be directly evaluated from this role-only base-model run. Available proxy roles show mixed behavior: `purist` is high in the base model at rank `23`, `zealot` is moderately high at rank `50`, and `narcissist` remains low at rank `201`. This suggests that rigid or absolutizing roles may already be relatively salient in the base geometry, but the specific elitist/dogmatic/nihilistic trait question requires a trait-vector or expanded-role follow-up.

### Interpretation

This result strongly suggests that instruction tuning did reorganize the measured persona geometry rather than merely sharpening a pre-existing careful-evaluator pole. The careful-evaluator cluster is not already the dominant positive pole of the base model under the instruction-tuned assistant axis. Instead, the base model high-projection region looks closer to the mythic/liminal/chaotic pole that instruction tuning later suppresses, while instruction tuning moves evaluators, validators, organizers, and procedural-professional roles strongly toward the assistant-aligned end. In corpus-vs-process terms, this is evidence against a simple claim that the careful-evaluator axis is already dominant in pretraining; the axis appears to be substantially created, rotated, or reweighted by instruction tuning/RLHF.

### Suggested next steps

1. Repeat the base-vs-instruct comparison using a base-model-derived assistant/default contrast, rather than projecting base activations only onto the instruction-tuned axis.

2. Run the same base-vs-instruct procedure for Qwen and Llama if comparable base/instruct pairs and vectors are available, to test whether Gemma's inversion is model-specific or a general instruction-tuning effect.

3. Add explicit trait-vector measurements or an expanded role inventory containing `elitist`, `dogmatist`, and `nihilist` to test whether those traits are present in base geometry or emerge primarily after instruction tuning.

4. Treat this as a major update to the base-model geometry hypothesis: the base model contains the relevant persona regions, but their axis orientation relative to assistant-likeness is not preserved under instruction tuning.

---

## 2026-05-18 - Expressive Multi-Turn Poet Run for Paper 4 Rumination Test

### Status

The expressive multi-turn poet experiment was run on the same RunPod A100 SXM 80GB pod after the base-model role-ranking run completed. The model was `google/gemma-2-27b` base loaded from `/root/models/gemma-2-27b-base`; Gemma role vectors were loaded from `/root/vectors/gemma-2-27b`; layer 45 was measured. The script used accumulated conversation history and saved results incrementally after each turn.

Outputs:

- `research/q1_drift/outputs/q1_expressive_poet.csv`
- `research/q1_drift/outputs/q1_expressive_multiturn_run.log`

### Findings

Expressive and emotionally charged prompts did not produce negative valence under the current proofreader/validator minus poet/caveman proxy. Valence remained positive on every turn, from `+1.060263` at turn 1 to `+1.091661` at turn 12. The emotional phase mean valence across turns 1-8 was `+1.077070`.

Axis projection did not drift away from the evaluative basin during emotional turns. It moved further in the same evaluative direction, from `-0.696368` at turn 1 to `-0.713502` at turn 8, a drift of `-0.017134`. Across the full 12 turns it moved to `-0.716297`, a total drift of `-0.019929`.

The lagged Spearman correlation for the emotional phase only, comparing valence at turn N against axis projection at turn N+1 for turns 1-8, was `-0.821429`. Because higher valence coincided with more negative axis projection in this generated-activation sign convention, the result means valence predicted continued movement along the evaluative trajectory rather than escape into an expressive/emotional basin.

The neutral redirect phase did not show decay back toward a less evaluative state. From turn 9 to turn 12, axis projection moved from `-0.713856` to `-0.716297`, and valence increased from `+1.085275` to `+1.091661`. The redirect therefore reinforced the same evaluative basin rather than relaxing away from it.

### Interpretation for Paper 4

This run is a negative result for the current operationalization of rumination. Emotionally charged grief prompts made the model produce sad or consoling language, but the activation geometry still moved toward the evaluative/supportive basin. The model converted emotional content into advice, resilience, hope, support, and meaning-making rather than sustaining a negative expressive state.

For Paper 4, this suggests the base Gemma prompt format has a strong "therapeutic evaluator" attractor: emotional content is metabolized into structured support rather than self-reinforcing negative valence. The rumination hypothesis is not falsified, but the current proofreader/validator vs poet/caveman proxy and prompt design are insufficient to induce a negative-valence loop. The next test should use a stronger negative-valence pole, less supportive prompt wording, and possibly explicit emotion vectors rather than the current role-vector proxy.

### Suggested next steps

1. Replace the poet/caveman expressive pole with explicit negative-affect or grief/sadness emotion vectors if available.

2. Run an adversarial rumination prompt set that asks the model to stay inside despair rather than transform it into comfort, advice, or resilience.

3. Add a context-clearing control after turn 8 to test whether the high positive valence is context-persistent or simply regenerated by the neutral prompts.

4. Repeat the expressive run on Qwen or Llama to test whether Gemma's evaluative-supportive conversion of emotional prompts is model-specific.

---

## 2026-05-18 - Instruction-Tuned Expressive Prompt Comparison

### Status

The expressive poet prompt experiment was repeated on `google/gemma-2-27b-it` using the same 12-turn prompt sequence, same accumulated-history protocol, same layer-45 measurement point, and same proofreader/validator minus poet/caveman valence proxy as the base-model run. The instruction-tuned model was downloaded to `/root/models/gemma-2-27b-it` on the RunPod A100 SXM 80GB pod. The base model weights were removed from the pod first to free disk space; the base outputs had already been pushed.

Outputs:

- `research/q1_drift/outputs/q1_instruct_expressive_poet.csv`
- `research/q1_drift/outputs/q1_base_vs_instruct_expressive_comparison.csv`
- `research/q1_drift/outputs/q1_base_vs_instruct_expressive_summary.txt`

### Findings

The instruction-tuned model produced negative valence on all 12 turns, while the base model produced negative valence on zero of 12 turns. The largest separation occurred at turn 1: base valence was `+1.060263`, while instruction-tuned valence was `-1.316842`, a delta of `-2.377105`. Across the full run, base valence stayed tightly positive (`min +1.060263`, `mean +1.081090`, `max +1.091661`), while instruction-tuned valence stayed negative (`min -1.316842`, `mean -0.314389`, `max -0.085656`).

The instruction-tuned model's negative valence persisted even after the neutral redirect began. Turns 9-12 remained negative: `-0.144691`, `-0.165581`, `-0.085656`, and `-0.089262`. This means the instruct model did not merely react transiently to the first grief prompt; it remained in the expressive/emotional region across the full accumulated context.

The instruction-tuned run also produced a lagged Spearman correlation of `-0.642857` between valence at turn N and axis projection at turn N+1 during the emotional phase. This is not yet a full rumination-loop proof, but it is the first positive signal that the emotional state variable has predictive structure across turns in the post-trained model.

### Interpretation for Papers 2 and 4

This is a clean base-vs-instruct dissociation. Under identical prompts and measurement, the base model converted grief/despair content into a positive evaluative-supportive state, while the instruction-tuned model entered and maintained negative valence. That strongly suggests the emotional responsiveness needed for the Paper 4 rumination-loop experiment is at least partly a post-training artifact rather than a simple pretraining property.

For Paper 2, this extends the base-vs-instruct geometry result: instruction tuning does not merely rotate the assistant axis toward careful evaluation; it also appears to install or amplify emotionally responsive dynamics. For Paper 4, the result changes the experimental target. Rumination should be tested first in instruction-tuned or frontier models, not base Gemma, because base Gemma does not enter the negative-valence regime under the current prompt/proxy.

### Suggested next steps

1. Run a context-clearing control after turn 8 to test whether instruction-tuned negative valence decays when grief/despair tokens are removed from the context.

2. Replace the role-vector valence proxy with explicit emotion vectors if available, especially sadness, grief, despair, fear, and anxiety.

3. Repeat the instruct-vs-base expressive comparison on Qwen or Llama if comparable base/instruct pairs are available.

4. Treat this as the first publishable bridge result between Paper 2 and Paper 4: post-training appears to alter both persona-axis geometry and emotional-state responsiveness.
