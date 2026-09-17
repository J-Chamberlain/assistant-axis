# AA-25 Stage 1 — Intervention-to-Big-Five transport

## Purpose

This stage asks whether the existing model trait spaces can represent the same broad trait directions that human intervention studies report. It is a representation test, not a causal model of intervention response.

The human literature supports the general idea that personality traits can change through intervention. Roberts et al. reviewed 207 studies and reported an average intervention-associated change around d=.37 over roughly 24 weeks, with the clearest changes in emotional stability and then extraversion. Volitional-change research also supports targeted movement through repeated trait-consistent behavior. These sources provide directions and intervention classes, not a universal effect size for every intervention and person.

## What was computed

The 240 model traits were assigned to Big Five domains using the frozen external-taxonomy mapping already used in the project. Neuroticism was polarity-reversed to emotional stability. Trait scores were standardized within model and averaged within each domain. These model-derived domain scores were compared with the existing human-anchored Big Five persona scores for all three models.

Five one-standard-deviation directional probes were then defined: emotional-stability therapy, social activation, behavioral activation, broad volitional growth, and openness training. Their HiFWB change is calculated from the frozen human Big Five–HiFWB coefficients. The one-unit size is a sensitivity convention, not a claim about a real dose.

## Interpretation boundary

This stage can tell us whether the model trait space contains usable Big Five-like directions and what human HiFWB would predict if a person moved along those directions. It cannot yet tell us whether a language model actually changes its trait profile after an intervention prompt, or whether that model-predicted change matches humans. That requires a later model-response or activation experiment and, ideally, human intervention data for validation.

## Artifacts

* `model_trait_derived_bigfive_scores.csv` — model-derived domain scores for 825 personas.
* `model_vs_human_bigfive_alignment.csv` — alignment with existing human-anchored scores.
* `intervention_directional_probes.csv` — frozen directional HiFWB probes.
* `trait_direction_mapping_used.csv` — exact trait-to-domain mapping used.

No model inference, RunPod, paid compute, or respondent-level data export occurred.
