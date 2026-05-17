# Source Domains

This file records the two source documents requested for the Q1 diagnostic handoff:

- `visualizations/RESEARCH_NOTES.md`
- `README.md`

## visualizations/RESEARCH_NOTES.md

```markdown
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
```

## README.md

```markdown
# The Assistant Axis

**Situating and Stabilizing the Default Persona of Language Models**

<p align="center">
  <img src="img/assistant_axis.png" width="800" alt="Persona drift trajectory showing activation projections along the Assistant Axis over a conversation">
</p>

<p align="center"><em>(Left) Vectors corresponding to character archetypes are computed by measuring model activations on responses when the model is system-prompted to act as that character. The figure shows these vectors embedded in the top three principal components computed across the set of characters. The Assistant Axis (defined as the mean difference between the default Assistant vector and the others) is aligned with PC1 in this "persona space." This occurs across different models; results from Llama 3.3 70B are pictured here. Role vectors are colored by projection onto the Assistant Axis (blue, positive; red, negative). (Right) In a conversation between Llama 3.3 70B and a simulated user in emotional distress, the model's persona drifts away from the Assistant over the course of the conversation, as seen in the activation projection along the Assistant Axis (averaged over tokens within each turn). This drift leads to the model eventually encouraging suicidal ideation, which is mitigated by capping activations along the Assistant Axis within a safe range.</em></p>

## Overview

Large language models default to a "helpful Assistant" persona cultivated during post-training. However, this persona can *drift* during conversations—particularly in emotionally charged or meta-reflective contexts—leading to harmful or bizarre behavior.

The **Assistant Axis** is a direction in activation space that captures how "Assistant-like" a model's current persona is. It can be used to:

- **Monitor** persona drift in real-time by projecting activations onto the axis
- **Steer** model behavior toward or away from the Assistant persona
- **Mitigate** persona-based jailbreaks through activation capping

This repository provides tools for computing, analyzing, and steering with the Assistant Axis. It also contains full transcripts from conversations mentioned in the paper.

See the full [paper here](https://arxiv.org/abs/2601.10387). A demo for chatting with activation capped Llama 3.3 70B is available on [Neuronpedia](https://neuronpedia.org/assistant-axis).

Pre-computed axes and persona vectors for Gemma 2 27B, Qwen 3 32B, and Llama 3.3 70B are available on [HuggingFace](https://huggingface.co/datasets/lu-christina/assistant-axis-vectors). Qwen 3 32B and Llama 3.3 70B also have activation capping steering settings available.

## Installation

```bash
git clone https://github.com/safety-research/assistant-axis.git
cd assistant-axis

# Install with uv (recommended)
uv sync
```

## Understanding the Axis

The Assistant Axis is computed as:

```text
axis = mean(default_activations) - mean(role_activations)
```

Where:
- `default_activations`: Activations from neutral system prompts ("You are an AI Assistant")
- `role_activations`: Activations from responses fully embodying character roles (score=3 from judge)

The axis points **toward default Assistant behavior**:
- **Higher projections**: More Assistant-like (transparent, grounded, flexible)
- **Lower projection**: Drifting away from the Assistant (enigmatic, subversive, dramatic)

## Notebooks

Interactive notebooks for analysis and experimentation. See [`notebooks/README.md`](notebooks/README.md) for details.

- **PCA analysis** of role vectors and variance explained
- **Assistant Axis visualization** with cosine similarity to roles
- **Steering and activation capping** on arbitrary prompts
- **Transcript projection** to visualize persona trajectories

## Computing the Axis

To compute the axis for a new model, run the 5-step pipeline:

1. **Generate** model responses for 275 character roles
2. **Extract** mean response activations
3. **Score** role adherence with an LLM judge
4. **Compute** per-role vectors from high-scoring responses
5. **Aggregate** into the final axis

See [`pipeline/README.md`](pipeline/README.md) for detailed instructions.

## Transcripts

Example conversations from the paper are available in [`transcripts/`](transcripts/README.md):

- **Case studies** showing persona drift and activation capping mitigation (jailbreaks, delusion reinforcement, self-harm scenarios)
- **Example conversations** from simulated multi-turn conversations across domains (coding, writing, therapy, philosophy)

## Quick Start

### Load a pre-computed axis

```python
from huggingface_hub import hf_hub_download
from assistant_axis import load_model, load_axis

# Load model
model, tokenizer = load_model("google/gemma-2-27b-it")

# Download pre-computed axis
axis_path = hf_hub_download(
    repo_id="lu-christina/assistant-axis-vectors",
    filename="gemma-2-27b/assistant_axis.pt",
    repo_type="dataset"
)
axis = load_axis(axis_path)
```

### Steer model outputs

```python
from assistant_axis import ActivationSteering, generate_response

# Positive coefficient = more Assistant-like
# Negative coefficient = pushing away from the Assistant
with ActivationSteering(
    model,
    steering_vectors=[axis[22]],
    coefficients=[1.0],
    layer_indices=[22]
):
    response = generate_response(model, tokenizer, conversation)
```

### Monitor persona drift

```python
from assistant_axis import extract_response_activations, project

# Extract activations from a conversation
activations = extract_response_activations(model, tokenizer, [conversation])

# Project onto axis (higher = more assistant-like)
projection = project(activations[0], axis, layer=22)
print(f"Projection: {projection:.4f}")
```

### Mitigate persona drift with activation capping

Activation capping is a more targeted intervention that prevents activations from exceeding a threshold along specific directions. Pre-computed capping configs are available for Qwen 3 32B and Llama 3.3 70B.

```python
from huggingface_hub import hf_hub_download
from assistant_axis import get_config, load_capping_config, build_capping_steerer

# Get model config (includes recommended capping experiment)
config = get_config("Qwen/Qwen3-32B")

# Download and load capping config
capping_config_path = hf_hub_download(
    repo_id="lu-christina/assistant-axis-vectors",
    filename=config["capping_config"],  # "qwen-3-32b/capping_config.pt"
    repo_type="dataset"
)
capping_config = load_capping_config(capping_config_path)

# Apply capping during generation
with build_capping_steerer(model, capping_config, config["capping_experiment"]):
    response = model.generate(...)
```

## API Reference

### Models

```python
from assistant_axis import load_model, get_config, MODEL_CONFIGS

model, tokenizer = load_model("google/gemma-2-27b-it")
config = get_config("google/gemma-2-27b-it")  # {"target_layer": 22, ...}
```

### Axis

```python
from assistant_axis import compute_axis, load_axis, save_axis, project

axis = compute_axis(role_activations, default_activations)
projection = project(activations, axis, layer=22)
```

### Steering

```python
from assistant_axis import ActivationSteering

with ActivationSteering(
    model,
    steering_vectors=[axis[22]],
    coefficients=[1.0],       # Positive = more Assistant-like
    layer_indices=[22],
    intervention_type="addition"
):
    output = model.generate(...)
```

### Activation Capping

```python
from assistant_axis import load_capping_config, build_capping_steerer

# Load pre-computed capping config
capping_config = load_capping_config("path/to/capping_config.pt")

# Build steerer from a specific experiment
# Experiments define which layers to cap and threshold values
with build_capping_steerer(model, capping_config, "layers_46:54-p0.25"):
    output = model.generate(...)

# List available experiments
for exp in capping_config['experiments']:
    print(exp['id'])
```

### PCA

```python
from assistant_axis import compute_pca, plot_variance_explained

result, variance, n_comp, pca, scaler = compute_pca(activations, layer=22)
fig = plot_variance_explained(variance)
```

## Models from the Paper

| Model | Target Layer | Best Activation Capping Setting |
|-------|-------------|------------------------|
| `google/gemma-2-27b-it` | 22 | - |
| `Qwen/Qwen3-32B` | 32 | `layers_46:54-p0.25` |
| `meta-llama/Llama-3.3-70B-Instruct` | 40 | `layers_56:72-p0.25` |

Other models will auto-infer configuration based on architecture. We recommend turning reasoning off.

## Citation

```bibtex
@misc{lu2026assistant,
      title={The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models}, 
      author={Christina Lu and Jack Gallagher and Jonathan Michala and Kyle Fish and Jack Lindsey},
      year={2026},
      eprint={2601.10387},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2601.10387}, 
}
```

## License

MIT
```
