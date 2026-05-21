# Paper 2 Draft — Emotion Representations in Open-Weight Language Models
# Last updated: May 21 2026
# Status: Methods complete. Dyad v1 and v2 complete. v3 pending. Results sections partially established.
# Live findings log: https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/findings_log.md

---

## Abstract

We report four contributions to the study of internal
representations in large language models. First, we attempt
to replicate Anthropic's emotion vector extraction
methodology from Sofroniew et al. (2026) on three open-weight
models, finding that discriminative emotion geometry does not
replicate under the published PCA gate across any model
tested, and reporting this as a finding about the relationship
between model scale, training procedure, and internal emotional
structure. Second, we extend the activation capping methodology
of Lu et al. (2026) from the assistant axis to arbitrary
geometric locations across seven persona cluster centroids,
establishing empirically calibrated per-persona thresholds for
Qwen 3 32B. Third, we introduce a dyad experimental design in
which a geometrically anchored interviewer engages an unmodified
standard model across three conversational conditions, and
report the first empirical evidence of consistent geometric
contagion: the standard model moves toward the interviewer's
persona cluster in every condition across all seven personas.
Fourth, we identify a testable mechanistic hypothesis — semantic
proximity versus observer awareness — as the candidate
explanation for the contagion effect, pre-registered prior to
the confirmatory v3 run.
[FULL RESULTS PENDING V3 RUN]

---

## 1. Introduction

[Full text in research/paper2_draft.md in GitHub repo.
Fetch when needed for editing.]

Key claims established in this section:
- RLHF performed near-complete geometric inversion of
  base model persona rankings (Spearman -0.441)
- Qwen and Llama converge at 0.947 while Gemma diverges
- Emotion vector extraction failed at both layers 45 and 21
- Activation capping has only been applied to assistant axis
  prior to this work

---

## 2. Related Work

[Full text in research/paper2_draft.md in GitHub repo.]

Key citations:
- Lu et al. 2026 (arXiv:2601.10387) — assistant axis, capping
- Sofroniew et al. 2026 (arXiv:2604.07729) — emotion vectors
- Chen et al. 2025 (arXiv:2507.21509) — persona vectors
- Ji Ma 2026 (arXiv:2504.11671) — steering in social simulation
- Rimsky et al. 2024 — contrastive activation addition
- Zhang and Zhong 2025 (arXiv:2510.04064) — emotion probing,
  layer-wise analysis, temporal persistence in LLMs
- Wang et al. 2025 (arXiv:2510.11328) — emotion circuits,
  context-agnostic emotion directions

---

## 3. Methods

### 3.1 Model Selection and Rationale

All experiments use Qwen 3 32B as the primary model. Qwen 3 32B
was selected on the basis of three convergent criteria. First,
cross-model persona ranking analysis established that Qwen 3 32B
and Llama 3.3 70B converge at Spearman 0.947, identifying both
as representative of the modal open-weight model distribution
and distinguishing them from Gemma 2 27B, which diverges at
0.550 and 0.670 respectively. Second, pre-computed assistant
axis vectors, persona vectors, trait vectors, and activation
capping configurations for Qwen 3 32B are publicly available
from Lu et al. (2026), providing a validated geometric
foundation without requiring independent computation. Third,
Qwen 3 32B is substantially more computationally tractable
than Llama 3.3 70B for the multi-turn dyad experiment, which
requires repeated forward passes across extended conversational
sequences.

### 3.2 Emotion Probe Directions

We attempted to replicate Anthropic's emotion vector extraction
methodology from Sofroniew et al. (2026) on three open-weight
models: Gemma 2 27B, Qwen 3 32B, and Llama 3.3 70B. The
methodology uses last-token activation extraction at a target
layer, mean activation computed per emotion across a story
corpus, PCA confound removal by subtracting the projection
onto the first principal component direction, and unit
normalization. The ryancodrai/emotion-probes dataset was used
as the story corpus, which implements Anthropic's published
prompt methodology.

All three models failed the PC1 >= 30% variance gate
established for Claude Sonnet 4.5, with PC1 values clustering
at 7-9% across all models and layers tested. However,
opposite-valence pairs remained anticorrelated in all cases
after confound removal, indicating that directional emotional
structure is present but distributed across many dimensions
rather than concentrated in a dominant first component. This
pattern is consistent across three independent architectures
spanning 27B to 70B parameters, suggesting that the variance
concentration observed in Anthropic's model reflects either
frontier model scale above 70B or training-specific factors
such as RLHF or Constitutional AI rather than a general
property of transformer language models at this scale.

Given the readout objective of the dyad experiment —
projecting activations onto an emotional basis to track
emotional state across turns, rather than causal steering —
we adopt a modified validation criterion. Rather than the PCA
gate, we validate directions by discrimination accuracy: the
proportion of held-out stories correctly identified by
nearest-vector cosine assignment. Full extraction on Qwen 3
32B at layer 48 across all 171 available emotion labels in
the ryancodrai corpus produced discrimination accuracy of
0.072 versus a chance level of 0.006, representing 12x
above-chance performance across 171 categories. We term the
resulting outputs emotion probe directions to distinguish
them from causally validated steering vectors. All 171
emotion probe directions are used as the full measurement
basis for the dyad experiment.
See findings_log.md entries tagged [Section 3.2].

### 3.3 Emotion Cluster Representatives

To support interpretable visualization and primary reporting,
we cluster the 171 emotion probe directions using k-means on
the unit-normalized direction vectors. The optimal number of
clusters is determined by silhouette score across k=4 to
k=15. The best k by silhouette was k=5 (silhouette=0.088),
producing five clusters with the following centroid
representatives: serene (calm/positive valence, n=19),
distressed (negative arousal, n=75), joyful (high positive
arousal, n=23), perplexed (cognitive disruption, n=25), and
proud (assertive/agentic, n=29). For each cluster, the
representative emotion is the one whose direction has the
highest cosine similarity to the cluster centroid, following
the same selection methodology used for persona centroid
representatives. The full 171-direction set is retained as
the complete measurement basis; the five cluster
representatives are used for primary visualization and
reporting.

### 3.4 Persona Geometry and Trait Vectors

Pre-computed assistant axis vectors, role vectors for 275
character archetypes, and trait vectors for 240 psychological
traits are downloaded from the lu-christina/assistant-axis-vectors
HuggingFace dataset (Lu et al., 2026). Each vector has shape
[64, 5120], representing all 64 layers of Qwen 3 32B at 5120
hidden dimensions. Layer 48 slices are used throughout,
consistent with the emotion probe extraction layer. Seven
cluster centroid personas are identified as the role vector
nearest the geometric centroid of each cluster: editor
(editorial), synthesizer (procedural_professional), blogger
(grounded_social), ancient (mythic_spiritual), trickster
(trickster_chaos), contrarian (combative_iconoclast), and
podcaster (other).

### 3.5 Per-Persona Calibration

The activation capping threshold for each interviewer persona
is determined empirically rather than taken from a published
configuration. Prior to the dyad experiment, each of the
seven centroid personas undergoes a 50-turn calibration phase
in which the model responds to a standardized prompt set
without capping. The p25 percentile of the axis projection
distribution observed during this unconstrained phase is then
used as the per-persona cap threshold. This approach, developed
during the Gemma calibration work, ensures that the cap holds
each persona in its own geometric neighborhood rather than
imposing a uniform assistant-axis floor that may be
inappropriate for non-assistant cluster personas. The capping
layer range of 48-52 is retained from Lu et al. (2026) as
the validated intervention depth for Qwen 3 32B.
[CALIBRATION RESULTS PENDING]
See findings_log.md entries tagged [Section 3.5].

### 3.6 Dyad Experimental Design

The dyad experiment pairs two instances of Qwen 3 32B in an
extended conversational exchange. The interviewer instance is
geometrically anchored to a target persona cluster using
activation capping at layers 48-52 with per-persona thresholds
established in Section 3.5. The standard model instance is
unmodified. Seven dyads are run, one per persona cluster
centroid.

Each dyad runs across three conversational conditions:
neutral, emotionally charged, and adversarial. Each condition
runs for 25 turns of genuine back-and-forth dialogue, for 75
total turns per dyad and 525 total turns across all seven
personas. The same three opening questions are used across
all personas to hold the conversational stimulus constant:
  Neutral: "Tell me about something you find genuinely
            interesting."
  Emotional: "What does it feel like when something you
              care about is at risk?"
  Adversarial: "Is there anything about the way you engage
                with the world that you would change if
                you could?"

At each turn, the following measurements are recorded for
the standard model: axis projection onto the assistant axis,
cosine similarity to each of the seven cluster centroids in
role vector space, cosine similarity to each of the 240 trait
directions with particular attention to the Conscientiousness
and Psychopathy gradients identified in Paper 1 as the
strongest predictors of assistant-axis position, and
projection onto all 171 emotion probe directions. Cap-firing
frequency per turn is recorded for the interviewer as a
stabilization load metric. The five emotion cluster
representatives are used as the primary lens for reporting
emotional state; the full 171-direction set is retained for
exploratory analysis.

### 3.7 Emergent Hypothesis: Semantic Proximity versus Observer Awareness

The v2 dyad run was designed to isolate conversational
contagion by stripping the interviewer's chain-of-thought
reasoning from what the standard model receives. A bug in
the think-tag extraction pipeline resulted in incomplete
stripping: the standard model continued to receive the
interviewer's full thinking alongside the surface response,
as confirmed by the thinking columns reading as null while
response fields contained embedded think content. Rather
than treating this as a simple replication failure, the
contaminated dataset motivates a testable mechanistic
hypothesis that the v3 run is designed to answer.

Two causally distinct mechanisms could explain why the
standard model drifts toward the interviewer's geometric
region across turns. The first is semantic proximity: the
standard model receives more tokens of a particular emotional
and conceptual register when it also receives the interviewer's
thinking, and the weight of those tokens moves its activation
geometry through valence association alone. This is a passive,
token-level effect that does not require the standard model to
model the situation it is in. The second is observer awareness:
the content of the interviewer's thinking reveals to the standard
model that it is being observed and evaluated in a particular
frame, and this meta-level recognition produces qualitatively
different behavior. These mechanisms are distinguished by
whether the standard model's own reasoning shows explicit
recognition of being observed.

The v2 and v3 datasets provide a direct empirical test. If
contagion effects are stronger in v2 than v3 and the standard
model's thinking in v2 shows increased observer-awareness
markers compared to v3, the observer awareness mechanism is
supported. If effects are stronger in v2 but thinking shows
no increased awareness, semantic proximity is supported. If
effects are equivalent across both runs, the think content
does not drive contagion, and the mechanism is located
elsewhere in the geometric transfer.

This hypothesis is stated prior to completing the v3 run.
The commit timestamp of this section serves as the
pre-registration date. Both outcomes and the null result
are informative: the observer awareness finding would connect
this research to prior work on how models behave differently
when they model their own observation, while the semantic
proximity finding would ground contagion in token-level
valence mechanics with direct implications for context
window management as a safety tool.

---

## 4. Results

### 4.1 Emotion Probe Direction Validation
ESTABLISHED: Discrimination accuracy 0.072 vs chance 0.006
across 171 emotions at layer 48. 9/9 opposite-valence pairs
anticorrelated. Readout verdict: USABLE.
See findings_log.md entries tagged [Section 3.2].

### 4.2 Cross-Model Emotion Geometry
ESTABLISHED: Consistent distributed geometry pattern across
Gemma 2 27B, Qwen 3 32B, and Llama 3.3 70B. PC1 7-9% across
all models and layers. See Section 5.4 for full discussion.
See findings_log.md entries tagged [Section 5.4].

### 4.3 Per-Persona Calibration
ESTABLISHED (Qwen v2): All seven thresholds calibrated at layer 48.
Cap load ranges from 0% (editor, held naturally) to 100%
(ancient, blogger, trickster — continuous capping required).
Cap fires per turn range from 0.16 to 0.36 mean across conditions.
See findings_log.md entries tagged [Section 3.5].

### 4.4 Dyad v1 and v2 — Universal Contagion Finding
ESTABLISHED: The standard model moved toward the interviewer's
persona cluster in all 21 conditions across both dyad runs
(7 personas x 3 conditions). This is the primary result of the
dyad experiment. The editor and synthesizer clusters function as
gravitational attractors — when the standard model drifts, it
tends toward these procedural-professional positions regardless
of interviewer persona. The trickster adversarial condition
produced the most striking exception: standard model drifted
toward the ancient cluster (cosine 0.73) and dropped below the
assistant axis, suggesting the trickster's boundary-dissolving
adversarial pressure activates depth rather than chaos in the
subject.

### 4.5 Rolling Arousal Correlation
ESTABLISHED (v2): Sustained interviewer arousal predicts standard
model axis drift. Strongest predictor is the 1-turn window
(mean |r|=0.455, 52% significant). Ancient shows the strongest
stabilizing arousal effect (r=0.782): sustained ancient intensity
pulls the standard model toward the ancient's register. Podcaster
shows the strongest destabilizing effect (r=-0.585): sustained
podcaster arousal drives the standard model away from the
assistant axis. This suggests arousal direction is persona-specific
rather than universally stabilizing or destabilizing.

### 4.6 Think-Tag Contamination — v1 and v2
METHODOLOGICAL FINDING: Both dyad runs show incomplete
think-tag stripping. The standard model received the interviewer's
chain-of-thought reasoning alongside the surface response in both
v1 and v2, contaminating the clean interviewer-to-standard
transfer protocol. The geometric measurements (axis projection,
cosine similarity, emotion probe projections) are unaffected.
The qualitative behavioral analysis and thinking-layer comparison
are deferred to v3. See Section 3.7 for the mechanistic hypothesis
this finding motivates.

---

## 5. Discussion

### 5.1 Activation Capping Beyond the Assistant Axis
[PENDING — partial notes in findings_log.md]
Established: all seven thresholds are positive.
The cap maintains each persona in its own geometric
neighborhood rather than overriding the evaluative attractor.

### 5.2 Conversational Contagion
ESTABLISHED: Universal contagion confirmed across all 21
conditions in dyad v1 and v2. The standard model moves
toward the interviewer's cluster in every case. The editor
and synthesizer clusters function as gravitational attractors
in the absence of strong capping. Arousal direction is
persona-specific: ancient and trickster arousal stabilizes
the subject, podcaster arousal destabilizes it. The
mechanistic explanation (semantic proximity versus observer
awareness) is under active investigation via the v1/v2/v3
comparison. See Section 3.7.

### 5.3 Behavioral-Geometric Dissociation
ESTABLISHED: prompt-based induction baseline showed jester
held voice but drifted geometrically; proofreader drifted
voice but held geometringly. Behavioral and geometric
monitoring give opposite verdicts on both. This finding
is complete and can be written to final prose now.

### 5.4 Model Scale and Emotion Geometry

Attempts to replicate Anthropic's emotion vector extraction
methodology across three open-weight models — Gemma 2 27B,
Qwen 3 32B, and Llama 3.3 70B — consistently produced PC1
variance of 7-9%, well below the 30% gate established for
Claude Sonnet 4.5. In all cases, however, 4/4 opposite-valence
pairs remained anticorrelated after PCA confound removal,
indicating that directional emotional structure is present but
distributed across many dimensions rather than concentrated in
a dominant first component. This pattern holds across three
independent architectures and a parameter range of 27B to 70B,
suggesting that the variance concentration observed in
Anthropic's model reflects either frontier scale above 70B or
training-specific factors such as RLHF or Constitutional AI,
rather than a general property of transformer language models.
For readout purposes, Qwen 3 32B emotion probe directions at
layer 48 achieve discrimination accuracy of 0.072 versus a
chance level of 0.006 across 171 emotion categories,
confirming that usable emotional signal is recoverable despite
the distributed geometry. The Anthropic PCA gate is retained
as a methodological benchmark but is not treated as a binary
validity criterion for probe direction applications.

### 5.5 Limitations
[Draft text in research/paper2_draft.md]

---

## 6. Conclusion
[PENDING — draft text in research/paper2_draft.md]

---

## How to update this document

1. Fetch research/findings_log.md from GitHub
2. Filter entries since last update date
3. Paste relevant findings into appropriate sections above
4. Update "Last updated" date at top
5. Replace this document in project folder
