# Axis Interpretation Method Sequence

Model used for synthesis: GPT-5.5.

## Purpose

This note records how the current PC1 and PC2 interpretations emerged. The method developed iteratively; the present forcing-function language should be treated as a hypothesis distilled from multiple analyses, not as a first-pass label.

## Sequence

1. **Initial persona-space inspection**
   PCA rankings, cluster structure, and visual geometry identified broad endpoint patterns. PC1 appeared related to assistantness, procedural professionalism, and careful evaluation. PC2 appeared related to abstraction, development, mythic structure, and reactive immediacy.

2. **Semantic and prompt-space baselines**
   Prompt-space semantic analyses showed that role prompt text contains real topology, but semantic structure alone does not fully explain activation geometry. The semantic baseline for predicting canonical activation PCA3D was around R2 0.389.

3. **Trait and procedural feature models**
   Big Five-style features improved prediction to around R2 0.613. Procedural features reached around R2 0.490. These results supported a layered model rather than a single semantic explanation.

4. **Hierarchical and lexical/register models**
   Richer combined models improved further, with SVD15 lexical/register features plus semantic and Big Five-style features reaching around R2 0.707. This suggested that prompt register and operationalization details explain additional residual structure.

5. **Axis validation studies**
   Reading-based and professional-hierarchy validation strengthened PC1 as a constraint/procedure/objective-certainty axis. PC2 remained weaker under the original "coherent action under uncertainty" interpretation.

6. **Conditional PC2 validation**
   After controlling approximately for PC1, abstraction became the strongest residual PC2 predictor. This moved PC2 away from "uncertainty tolerance" and toward integrated abstraction versus developmental/reactive situatedness.

7. **Cone and void observations**
   Persona-space visualization suggested that high PC1 compresses variation in PC2/PC3 while lower PC1 opens broader geometric degrees of freedom. This supported reframing PC1 as convergence pressure versus admissible degrees of freedom.

8. **Trait-vector and trait-space analyses**
   Persona coordinates were reconstructible from persona-trait cosine profiles at near-ceiling performance, but direct trait-space PCA only partially aligned with persona PCA. This strengthened the shared-geometry claim while warning against reducing persona axes to direct trait axes.

9. **Prompt-to-geometry forecasting**
   Leakage-controlled prompt text predicted held-out trait geometry with mean R2 0.389 and held-out role geometry with mean R2 0.621. Axis interpretation therefore became directly relevant to forecasting-rubric design.

## Current PC1 Hypothesis

PC1 is currently interpreted as convergence pressure versus degrees of freedom.

Evaluator-like roles are evidence for this interpretation, not the interpretation itself. High PC1 constrains the role toward correct-answer or procedural convergence; low PC1 admits broader symbolic and expressive self-consistent continuations.

## Current PC2 Hypothesis

PC2 is currently interpreted as integrated abstraction versus situated developmental immediacy.

The key addition is admissibility: some personas cannot coherently occupy deep integrated abstraction because their defining role lacks the prerequisites for reflective synthesis or accumulated world-model structure.

## Numerical Context To Preserve

- Semantic baseline: around R2 0.389.
- Procedural features: around R2 0.490.
- Big Five-style features: around R2 0.613.
- Richer combined models: around R2 0.707.
- Prompt-to-geometry forecasting, held-out traits: PC1 R2 0.414, PC2 R2 0.304, PC3 R2 0.450.
- Prompt-to-geometry forecasting, held-out roles: PC1 R2 0.783, PC2 R2 0.577, PC3 R2 0.504.

## Caveat

The forcing-function interpretation should not be presented as established causality. It is the current best geometric interpretation to operationalize and test through prompt-level judge rubrics and held-out forecasting improvement.
