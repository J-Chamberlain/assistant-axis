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
