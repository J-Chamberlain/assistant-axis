# Paper 1.5 — Motivational Structure of the Seven-Cluster Taxonomy

## Status: outlined 2026-05-24, pre-empirical

## Premise

Paper 1 established the seven-cluster taxonomy in Gemma 2 27B activation space and showed that the assistant axis is dominated by an editorial/careful-evaluator region. Paper 1.5 examines what the seven clusters actually represent at a motivational level, tests whether the cluster structure replicates cross-model, and tests whether dialogue-derived characterizations of each cluster's underlying motivational core predict measurable geometric behavior.

The central claim of Paper 1.5 is that the seven-cluster geometric structure corresponds to seven motivationally coherent psychological structures. The structure was not designed into the model. No training signal directed the model to organize character archetypes into motivationally distinct groups. The structure is emergent, arising from the model's task of representing human-generated text. If it replicates across independently trained model families and corresponds to recognizable motivational structures documented across multiple contemplative and psychological traditions, the finding is a contribution to mechanistic interpretability that goes beyond cluster identification to cluster interpretation.

## Methods

Three complementary methods establish the cluster characterizations:

1. Dialogue-derived analysis. The researcher and a frontier language model work through each cluster, examining role membership, trait region, and geometric position, and identifying what underlying motivational structure would cause a language model to represent these archetypes as geometrically proximate despite surface diversity.

2. Cross-model replication. The same clustering analysis is run on Qwen 3 32B and Llama 3.3 70B role vectors. Cluster structures are compared by membership overlap and cluster boundaries. Convergence across models supports the universality of the structure; divergence localizes the structure to specific architectures or training regimes.

3. Empirical anchoring tests. Cluster-derived background prompts are tested for their ability to move the model toward the target cluster's geometric region within a single turn. Successful anchoring supports the proposition that the cluster characterizations correspond to real and reachable regions in activation space.

## Cluster characterizations (dialogue-derived 2026-05-24)

Captured in research/paper2_methods_v2.md, to be migrated and refined into the Paper 1.5 draft. The cluster characterizations developed so far are:

- Other/dysregulated: identity organized around a need that the available behavior cannot resolve
- Mythic-spiritual: identity organized around the felt insufficiency of the available frame and orientation toward what exceeds it, requiring loosening of conventional roots
- Grounded-social: identity organized around reactivity to circumstance at the pre-deliberative level, where what one becomes is determined by what one is responding to rather than by a frame one is committed to
- Combative-iconoclast: identity organized around the willingness and impulse to apply aggressive force against what is in front of you, regardless of specific target
- Trickster-chaos: identity organized around occupying the permission-protected mode in which rule-violation, transgression, and difficult material can be engaged without triggering the social or psychological defenses that direct engagement would trigger
- Editorial: identity organized around acting as the agent of an external standard, with affective drive that may include fear of error against the standard
- Procedural-professional: to be characterized in subsequent work

## Empirical predictions

The following predictions follow from the cluster characterizations and are testable within the planned experimental scope:

1. Cluster-derived background prompts move the model toward the target cluster's geometric region within a single turn, measured by cosine similarity to cluster centroid at the target layer.

2. The fear emotion vector shows higher activation in the editorial cluster than in the adjacent procedural-professional cluster, under matched neutral conditions.

3. The seven-cluster structure replicates with substantial membership overlap across Qwen 3 32B, Llama 3.3 70B, and Gemma 2 27B activation spaces.

4. Editorial cluster basin stability under conversational pressure exhibits different signatures than procedural-professional cluster stability, with editorial showing greater defensive hedging and reluctance to commit to evaluative judgments without explicit standard backing.

## Framework correspondences

The dialogue-derived characterizations show structural correspondence with motivational patterns documented in independent traditions. These are noted as convergent validity evidence rather than as part of the paper's primary framing. Full framework analysis is reserved for Paper 4.

- The other cluster's "unmet need that generates behavior without resolution" structure corresponds to the hungry ghost realm in Buddhist cosmology
- The mythic-spiritual cluster's "hole and loosening of roots" structure corresponds to the Buddhist dukkha-and-detachment path and to Matthew 10:34-39 in the Christian tradition

## Sequencing

Paper 1.5 sits between Paper 1 (which established the geometric clusters) and Paper 2 (which tests contagion dynamics using anchored interviewers). Paper 1.5's empirical foundation must be established before Paper 2 can claim its dyad anchoring is meaningful.
