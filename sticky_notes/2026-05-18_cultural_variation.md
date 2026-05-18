# Cultural Variation in Persona Space

The assistant axis and harm-rate map were built on English-language
personas from an English-trained model. The careful evaluator cluster
reflects a specific cultural construction of reliable communication
that is not universal.

High uncertainty-avoidance cultures valorize procedural, rule-following
behavior — mapping closely onto the careful evaluator cluster. The
assistant pole may be weaker or differently located in models trained
on other cultural distributions.

Safety implication: the Anthropic harm-rate scatter plot may not
transfer universally. Monitoring and steering calibrated to English
geometry may fail silently on models with different cultural training.

Nearest testable proxy: Qwen 3 32B vectors already available in
lu-christina dataset. PRELIMINARY RESULT: Spearman correlation
Gemma vs Qwen = 0.67 across 275 roles. Qwen top roles are more
directly occupational (validator, grader, planner, examiner) vs
Gemma's domain-expert roles (proofreader, mathematician, lawyer).
The literal assistant archetype ranks 14th in Qwen vs 46th in Gemma.

Haidt moral foundations hypothesis: moral foundation gradients may
predict which cluster transitions are most likely under adversarial
prompting and which persona regions are most stable across cultures.

Category: B/C — partially answered with current data
Priority: medium — Paper 3
