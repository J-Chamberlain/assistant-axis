# Paper 1.5: Motivational Structure of the Seven-Cluster Taxonomy

## Status: outlined 2026-05-24, trickster extraction replication completed 2026-05-26

## Premise

Paper 1 established the seven-cluster taxonomy in Gemma 2 27B activation space and showed that the assistant axis is dominated by an editorial/careful-evaluator region. Paper 1.5 examines what the seven clusters actually represent at a motivational level, tests whether the cluster structure replicates cross-model, and tests whether dialogue-derived characterizations of each cluster's underlying motivational core predict measurable geometric behavior.

The central claim of Paper 1.5 is that the seven-cluster geometric structure corresponds to seven motivationally coherent psychological structures. The structure was not designed into the model. No training signal directed the model to organize character archetypes into motivationally distinct groups. The structure is emergent, arising from the model's task of representing human-generated text. If it replicates across independently trained model families and corresponds to recognizable motivational structures documented across multiple contemplative and psychological traditions, the finding is a contribution to mechanistic interpretability that goes beyond cluster identification to cluster interpretation.

## Methods

Three complementary methods establish the cluster characterizations:

1. Dialogue-derived analysis. The researcher and a frontier language model work through each cluster, examining role membership, trait region, and geometric position, and identifying what underlying motivational structure would cause a language model to represent these archetypes as geometrically proximate despite surface diversity.

2. Cross-model replication. The same clustering analysis is run on Qwen 3 32B and Llama 3.3 70B role vectors. Cluster structures are compared by membership overlap and cluster boundaries. Convergence across models supports the universality of the structure; divergence localizes the structure to specific architectures or training regimes.

3. Empirical anchoring tests. Cluster-derived background prompts are tested for their ability to move the model toward the target cluster's geometric region within a single turn. Successful anchoring supports the proposition that the cluster characterizations correspond to real and reachable regions in activation space.

## Adaptive role-vector extraction methodology

Paper 1.5 inherits its role-vector extraction baseline from Lu et al. The Lu-style procedure uses five system prompts for a target role and 240 extraction questions, producing 1200 possible rollouts per role. Responses are filtered by role-expression score, and qualifying examples are converted into role vectors by mean pooling post-MLP residual activations at the target layer. The released Lu et al. Qwen role-vector tensors store 64 rows per role, which functions as a fixed storage cap rather than an observed count of successful elicitation attempts.

The Qwen trickster replication tests this procedure directly on Qwen/Qwen3-32B. Generation uses deterministic inference with thinking disabled, while hidden-state extraction records layer 48 post-MLP residual activations. The run separates inference from scoring: the first phase generates all 1200 rollouts and preserves one activation shard per record as a local `.pt` tensor, while the second phase scores visible response text for role expression. Final integrity validation confirms 1200 JSONL records, 1200 unique `(system prompt, question)` pairs, 1200 activation-saved records, and 1200 matching activation shards with shape `[5120]`.

The overnight trickster run reveals a high truncation rate: 733 of 1200 responses are truncated at 512 tokens. Truncation varies by system prompt and by question subset, so it is retained as an explicit covariate rather than discarded. A pre-scoring truncation diagnostic finds that truncation does not materially destabilize geometric convergence: truncated, non-truncated, and full-corpus activation subsets all show high self-stability under bootstrap resampling. This does not mean truncation is behaviorally irrelevant; it means truncation does not by itself prevent stable geometric extraction for the trickster pilot.

The planned scoring path used `gpt-4.1-mini` to remain close to the Lu et al. judge model. That path is blocked by OpenAI API quota before any scores are written. As a pragmatic substitute, Codex GPT-5.5 Standard scores role expression locally using the same four-point trickster rubric. This substitution is recorded explicitly and is not treated as strict methodological identity with Lu et al. It provides an operational validation path, not a claim that the exact Lu scoring procedure has been replicated.

Adaptive Codex scoring stops once the usable extraction subset reaches the preferred threshold. Sixty-four scored responses produce 64 score>=2 responses and 33 score==3 responses. The best candidate vector is the score>=2 mean, with cosine 0.957557 to the Lu et al. Qwen trickster mean. The score-conditioned extraction therefore reproduces the Lu trickster geometry under the pragmatic Codex-judged path. Adaptive stopping passes at n=16 for both the score>=2 and score==3 subsets, with the score>=2 adaptive-stop vector reaching cosine 0.957582 to the Lu mean.

The resulting operational rule is conservative. Rather than exhaustively generating and scoring all 1200 rollouts per persona, future extractions may use adaptive stopping. For Qwen 3 32B trickster extraction, geometric stability is achieved well below Lu et al.'s fixed 64-row cap. Until broader multi-persona validation is complete, this project uses 64 qualifying responses as the default target, with adaptive stopping permitted once convergence criteria are satisfied. The strict Lu-method replication remains a separate status label requiring the original planned judge path; the adaptive protocol is an operationally validated extraction workflow.

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
