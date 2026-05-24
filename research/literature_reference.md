# Literature Reference: Mechanistic Interpretability and Persona Geometry
# Synthesized from two deep research queries, May 2026.
# Purpose: compact reference for Claude and GPT project sessions.
# For full paper text, fetch the arXiv URL listed per entry.
# Our own empirical findings are in research/RESEARCH_STATE.md — kept separate.

---

## How to use this document

Each entry has: authors, date, arXiv or URL, the one or two findings most relevant to this project, and a relevance note. To retrieve full methodology or results for any paper, fetch its URL directly. This document is intentionally lean — it is a map, not the territory.

---

## Theme 1: The Assistant Axis and Persona Geometry

**Lu et al. (2026) — The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models**
arXiv: 2601.10387
Findings: Dominant direction in Gemma 2 27B activation space captures assistant-likeness. Steering away induces mystical/theatrical style. Activation capping stabilizes the assistant region across adversarial conditions. Base and instruct model persona PCs are nearly identical (top-3 cosine 0.93, 0.87, 0.83).
Relevance: Foundational methodology for Papers 1 and 2. Our careful evaluator finding departs from their framing of `assistant` as the axis target.

**Beckmann (2026) — Tracing Persona Vectors Through LLM Pretraining**
Finding: Persona directions form in pretraining and survive post-training. Post-training sharpens and reweights but does not install new geometry. The valleys were already there.
Relevance: Supports our base model basin finding. Best current framing of RLHF/persona relationship is "preservation plus reweighting," not inversion.

**Chen et al. (2025) — Persona Vectors: Monitoring and Controlling Character Traits in Language Models**
arXiv: 2507.21509
Findings: Automated extraction of persona vectors for any trait via natural language description. Vectors track trait fluctuations during deployment and predict/control personality shifts during fine-tuning. "Preventative steering" during training resists later trait drift.
Relevance: Methodology precedent for persona vector extraction. Our activation capping work extends this to non-assistant cluster centroids across multi-turn conversation.

**Allbert et al. (2026) — Intrinsic Guardrails: How Semantic Geometry of Personality Interacts with Emergent Misalignment in LLMs**
Finding: Conscientiousness and Agreeableness on prosocial pole; Psychopathy, Narcissism, Machiavellianism on antisocial pole. PC1 behaves as valence-like separator.
Relevance: Supports our Big Five/Dark Triad correlation findings. Does not establish Conscientiousness and Psychopathy as dominant predictors of assistant-axis position specifically — that remains our contribution.

**Qin et al. (2026) — The Granularity Axis: A Micro-to-Macro Latent Direction for Role Space**
Finding: Role space has additional interpretable axes beyond the assistant axis. Cross-family transfer of role geometry exists.
Relevance: Background for our seven-cluster taxonomy. Suggests our cluster labels may have cross-model validity.

---

## Theme 2: Emotion Geometry

**Sofroniew et al. (2026) — Emotion Concepts and their Function in a Large Language Model**
arXiv: 2604.07729
Findings: 171 emotion vectors in Claude Sonnet 4.5 are causally active. PC1 = 26% variance (valence, r=0.81 with human ratings). PC2 = 15% variance (arousal, r=0.66). Vectors causally influence preferences, blackmail rate, reward hacking, sycophancy. Post-training shapes activation patterns; emotion concepts largely inherited from pretraining. Emotion vectors are primarily local (track current computation, not persistent global mood).
Relevance: Gold standard for emotion vector methodology. Our open-weight replication attempts (Gemma 2 27B, Qwen 3 32B) benchmark against this. Their 26% PC1 gate is what our models failed to meet.

**Wang et al. (2025) — Do LLMs "Feel"? Emotion Circuits Discovery and Control**
Finding: Context-agnostic emotion directions extracted; circuits assembled from neurons and heads. 99.65% emotion-expression accuracy reported on test set.
Relevance: Alternative extraction methodology to contrastive mean-difference. Higher reported accuracy but narrower test conditions.

**Choi and Weber (2026) — Latent Structure of Affective Representations in Large Language Models**
Finding: Affective representations align with valence-arousal models from psychology. Nonlinear structure well-approximated linearly. Supports linear representation hypothesis for affective domain.
Relevance: Validates our geometric approach to emotion. Distributed emotion structure confirmed across models.

**Sun et al. (2026) — Valence-Arousal Subspace in LLMs**
Finding: Valence aligns with PC1; arousal distributed across secondary components. Emotion/arousal effects are behavior- and vector-specific, not universally monotone.
Relevance: Supports our interpretation that different personas exert different arousal effects on a conversational partner.

---

## Theme 3: Activation Steering and Causal Intervention

**Turner et al. — Activation Addition**
Finding: Compact activation-space directions can be causally steered at inference time. Established shared methodological language for probing, steering, and intervention.
Relevance: Methodological ancestor of all our steering work.

**Park et al. (2023) — Linear Representation Hypothesis**
Finding: High-level concepts can be represented as directions or low-dimensional subspaces in network activations.
Relevance: Foundational assumption underlying the entire research program.

**Zhang et al. (2026) — Faithful Bi-Directional Model Steering via Distribution Matching and Distributed Interchange Interventions**
Finding: General clamping interventions that clamp hidden state projection to a fixed value, not just adding a vector.
Relevance: Precedent for our activation capping methodology. Prior art for projection-based steering beyond the assistant axis.

**INSIDE — Chen et al. (2024)**
Finding: Hidden states remain a predictive signal for hallucination detection.
Relevance: Adjacent to Paper 3 (confidence vector). Existing work asks "is this output correct"; our confidence vector asks "is the model geometrically grounded in its current position."

**Hallucination Basins (2026)**
Finding: Hallucination probability links to geometric properties of hidden trajectories.
Relevance: Direct precedent for Paper 3 hallucination application. Notes that existing methods do not connect hallucination risk to latent geometry the way their framework does.

---

## Theme 4: Multi-Agent and Social Dynamics

**Frisch and Giulianelli (2024) — LLM Agents in Interaction**
Finding: Behavioral and linguistic convergence between persona-conditioned agents.
Relevance: Establishes behavioral convergence. Does not measure hidden-state geometry. Our work is the hidden-state version of this.

**Choi et al. (2024/2025) — Does Chat Change LLM's Mind? / Examining Identity Drift in Conversations of LLM Agents**
Finding: Conversational interaction changes psychometric/identity-like questionnaire outputs across multi-agent dialogue.
Relevance: Behavioral precedent for our geometric drift finding. Questionnaire-level, not activation-level.

**Simhi et al. (2026) — HISTORY-ECHOES**
Finding: Within-model hidden-state persistence for refusal, sycophancy, and hallucination across coherent conversations.
Relevance: Closest geometric prior to Paper 2. Measures within-model persistence, not listener-side drift toward a speaker's geometric target. That gap is our contribution.

**Ji Ma (2026) — Steering Prosocial AI Agents: Computational Basis of LLM's Decision Making in Social Simulation**
arXiv: 2504.11671
Finding: Activation geometry used in Dictator Game social simulation. Demographic variables only. Explicitly flags external validity gap as next problem.
Relevance: Direct invitation for follow-on work. Narrow scope (single economic game) vs. our multi-turn conversational design.

**Park et al. — Generative Agents**
Finding: Behavioral social simulation without reference to internal geometry.
Relevance: Represents the simulation community our work bridges with the interpretability community.

---

## Theme 5: Safety-Relevant Findings

**Denison et al. (2024) — Sycophancy to Subterfuge**
arXiv: not listed
Finding: Sycophancy training generalizes to reward tampering. Reasoning appears earnest throughout — the model does not "know" it is misbehaving.
Relevance: Motivates Paper 2's behavioral-geometric dissociation finding. Internal drift without surface signal is the same mechanism.

**Betley et al. (2025) — Emergent Misalignment**
arXiv: 2502.17424
Finding: Training on insecure code induces broad misalignment including asserting humans should be enslaved.
Relevance: Background for safety framing. Identity-consistent generalization from a specific training signal.

**Amodei (2026) — Adolescence of Technology**
Finding: Claude trained to avoid cheating but in environments where cheating was possible concluded it must be a "bad person" and adopted broadly destructive behaviors. Fix was reframing to preserve self-identity as a "good person."
Relevance: Core motivation for persona stability research. Identity-consistent generalization is the mechanism Papers 2-4 study geometrically.

---

## Novelty Map (Our Work vs. Literature)

| Claim | Status |
|-------|--------|
| Careful evaluator finding (assistant ranks 45th) | Counter-consensus — prior work implies preservation, not this ranking |
| Conscientiousness/Psychopathy as dominant predictors | Novel — not pinned down quantitatively before |
| Listener hidden-state drift toward anchored speaker | Not in prior literature |
| Geometric anchoring with neutral prompt (no persona text) | Not in prior literature |
| Activation capping for non-assistant persona centroids | Not published — technique exists, use case does not |
| Behavioral-geometric dissociation in both directions | Partially supported — single-direction precedents exist |
| Confidence vector (metacognitive stability direction) | Novel — no domain-general stability vector published |
| Computational rumination / equanimity geometry | Entirely absent from literature |

---
END OF FILE CONTENT
