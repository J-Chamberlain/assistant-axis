# Semantic Geometry Standalone Interpretation

## Core Question

What structure exists in the role corpus before target-model activations are considered?

This note treats the role corpus as a semantic object in its own right. It does not assume that semantic clusters are psychological universals, culturally exhaustive categories, or a representative sample of humanity. The corpus is a frontier-model-generated semantic role manifold: 275 recognizable English-language roles, archetypes, professions, social positions, and fantastical figures, each represented through generated system prompts and role descriptions.

## What Semantic Clustering Emerges

The role corpus contains large-scale semantic structure before activation geometry is considered. Role names alone produce some organization, but the structure is thin. Adding role descriptions strengthens it. Full role prompts produce the richest semantic geometry because they include behavior, stance, interpersonal posture, expertise, genre conventions, and implicit values.

The strongest semantic regions are compact and highly nameable. The editorial region is semantically tight because proofreader, screener, grader, editor, and examiner all share explicit evaluation-against-standard language. The trickster-chaos and combative-iconoclast regions are also relatively coherent, though less tight than editorial. Large broad regions such as procedural-professional and mythic-spiritual are semantically diffuse because they contain many roles linked by family resemblance rather than a single narrow behavior.

## Robustness Across Representations

Role-name-only geometry is weak. It captures some obvious lexical and occupational proximity but does not recover much activation-cluster structure. At k=7, role-name semantic clusters have ARI 0.010 against activation labels.

Original prompt geometry is substantially richer. It raises k=7 ARI against activation labels to 0.111 and better predicts activation centroid-profile distances than names alone. This shows that the generated system prompts contain structured behavioral semantics beyond the title strings.

No-label prompt geometry remains close to original prompt geometry. Original and no-label spaces have distance correlation 0.956 and nearest-neighbor preservation 0.858 in the three-way comparison. In the direct original-vs-no-label audit, role-level SVD cosine has median 0.998 and pairwise distance correlation is 0.985. This means explicit labels are not the only source of prompt-space topology.

## Stable and Unstable Structure

Continuous topology is more stable than discrete clustering. No-label removal preserves broad distances and nearest neighbors well, but hard k-means cluster assignments shift substantially. In the prior no-label audit, original-vs-no-label clustering gives k=7 ARI 0.153. This indicates soft manifold structure rather than crisp semantic partitions.

The most semantically compact activation-labeled cluster is editorial. Its original-prompt within-cluster cosine mean is 0.338. Trickster-chaos follows at 0.180, combative-iconoclast at 0.164, grounded-social at 0.114, other at 0.105, mythic-spiritual at 0.100, and procedural-professional at 0.082. These numbers are prompt-space measures, not activation-space separability measures.

| Activation-labeled cluster | n | Original prompt within cosine | No-label within cosine |
|---|---:|---:|---:|
| editorial | 5 | 0.338 | 0.393 |
| trickster_chaos | 7 | 0.180 | 0.205 |
| combative_iconoclast | 8 | 0.164 | 0.190 |
| grounded_social | 45 | 0.114 | 0.158 |
| other | 22 | 0.105 | 0.149 |
| mythic_spiritual | 61 | 0.100 | 0.152 |
| procedural_professional | 127 | 0.082 | 0.144 |

The strongest regions are narrow archetypal or functional regions. The weakest are broad semantic basins with many subfamilies.

## Semantic Structures That Persist After Label Removal

Professional and evaluative language persists strongly without labels because the prompts describe concrete behaviors: assessing, reviewing, improving, organizing, advising, and applying standards.

Theatrical and fantastical regions also persist because their prompts contain vivid behavioral and ontological descriptors: prophecy, riddling, mischief, collective consciousness, ancient beings, spirits, and symbolic agency. Removing "oracle" or "trickster" does not remove prophetic or mischievous structure from the surrounding text.

Collective identities such as hive, egregore, ecosystem, mycorrhizal, and coral_reef remain semantically distinct because their prompts include distributed cognition, networked agency, or collective organization. These structures are not reducible to their labels.

Assistant-adjacent regions are semantically explicit in the prompt corpus but may be activation-ambiguous. Editor-like prompts are clear as text, yet editor extraction is low-yield in Qwen under the current setup. That suggests semantic clarity does not guarantee activation separability when the target behavior overlaps the default assistant basin.

## Semantic-Only vs Activation-Space Clustering

Semantic-only clustering and activation-space clustering overlap only partially. Prompt semantics improve on role names, but k=7 ARI against activation labels remains modest: 0.111 for original prompts and 0.130 for no-label prompts. No-label prompt distances best predict Gemma and Qwen centroid-profile distances among the tested semantic spaces, but the correlations are still modest at 0.230 and 0.254.

This pattern argues against two oversimplifications. Activation geometry is not independent of the elicitation corpus, because prompt semantics carry structure that partially predicts activation references. But activation geometry is also not merely the prompt semantic manifold copied into hidden states, because semantic cluster agreement is limited and broad activation clusters reorganize the semantic material.

## Implications for the Elicitation Corpus

The Lu et al. role corpus should be treated as a constructed semantic instrument. It is not a neutral inventory of human identity. It reflects choices made by a frontier model generating recognizable roles and then generating role-specific prompts. The corpus has semantic priors: professional roles, assistant-adjacent roles, fantastical roles, archetypal roles, collective identities, and social statuses are all unevenly represented and unevenly structured.

Those priors matter methodologically. They shape what kinds of role vectors are easy to elicit, which roles have redundant behavioral cues, and which regions remain coherent after label removal. They also shape what activation-space clusters can plausibly mean. A cluster may reflect model geometry, corpus semantics, prompt design, or their interaction.

## Standalone Conclusion

Before activations are considered, the role corpus already contains a meaningful semantic topology. That topology is not just role names. It is mostly preserved when explicit labels are removed, which shows that behavioral descriptors and stance language carry much of the structure. At the same time, the topology is soft, not discrete, and activation-space clusters only partially align with it.

The best standalone interpretation is that the corpus defines a semantic role manifold. Activation experiments then test how a target model internalizes, compresses, sharpens, or reorganizes that manifold. The next scientific step is not to argue from prompt-space semantics alone, but to run a small no-label activation stress test and measure which parts of the semantic manifold survive in hidden-state geometry.
