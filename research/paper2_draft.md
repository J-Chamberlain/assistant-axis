# Emotion Representations in Gemma 2 27B: Replication, Geometry, and Persona Stability Under Conversational Pressure

Josiah Chamberlain
Independent Research, Washington D.C.
May 2026

---

## Abstract

We report three contributions to the study of internal
representations in large language models. First, we attempt
to replicate Anthropic's emotion vector extraction
methodology from Sofroniew et al. (2026) on Gemma 2 27B
instruction-tuned, finding that discriminative emotion
geometry does not replicate at layers 45 or 21 in this
model, and reporting this as a methodological finding
about model scale. Second, we characterize the relationship
between persona space and activation geometry in this model,
extending the calibration methodology of Lu et al. (2026)
from the assistant axis to arbitrary geometric locations
across seven persona cluster centroids. Third, we introduce
a novel dyad experimental design in which a geometrically
anchored interviewer, held in a specific non-assistant
persona using Anthropic's activation capping method, engages
an unmodified standard model across three conversational
conditions. We measure cap-firing frequency as a proxy for
stabilization load and track the standard model's persona
drift as a conversational contagion effect. [FINDINGS TO
BE COMPLETED ONCE DYAD EXPERIMENT RUNS.]

---

## 1. Introduction

Large language models maintain an internal representation
of the kind of entity they are being at any moment. This
representation is not fixed: it drifts across conversation
in response to emotional pressure, persistent prompting,
and the character of the interlocutor. Understanding where
that drift leads, and under what conditions it can be
controlled, is both a safety problem and an interpretability
problem.

Prior work has made progress on two fronts. Anthropic's
Assistant Axis study demonstrated that a dominant direction
in activation space captures how assistant-like a model's
current persona is, and that activation capping along this
direction reduces harmful responses by nearly 60% without
degrading capability. The same paper introduced activation
capping as a stabilization mechanism: rather than constantly
pushing the model toward the assistant end of the axis, the
method establishes a threshold from the normal range of
assistant behavior and only corrects when the activation
drifts below it. This avoids the coherence degradation that
plagues constant activation addition, which compounds
perturbations across the KV cache and produces incoherent
generation in multi-turn dialogue.

However, activation capping has only been applied to the
assistant axis. Whether the same method can maintain a model
in an arbitrary non-assistant geometric location across
extended multi-turn conversation is an open question. This
matters for two reasons. Practically, it would provide a
controlled experimental instrument: a model reliably held
in a specific character throughout a conversation, regardless
of what its interlocutor says. Theoretically, it would
establish whether the evaluative attractor identified in
prior work is the only stable basin in the instruction-tuned
model, or whether any geometric location can be made stable
with sufficient capping.

This paper also addresses a gap in the emotion representation
literature. Sofroniew et al. (2026) extracted 171 emotion
vectors from Claude Sonnet 4.5 and demonstrated that these
vectors are causally active. These vectors are not publicly
released, and no equivalent exists for open-weight models.
We attempt to replicate their extraction methodology on
Gemma 2 27B, finding that the valence-arousal structure
does not replicate in this model at either layer examined.
We report this as a finding about model scale: discriminative
emotion geometry may require frontier-scale models.

A base model versus instruction-tuned comparison provides
further context. The Gemma 2 27B base model shows a
Spearman correlation of -0.441 with the instruction-tuned
model's persona rankings, indicating that RLHF performed
a near-complete geometric inversion rather than amplifying
existing tendencies. The base model prefers mythic and
chaotic personas naturally; instruction tuning elevated
the careful evaluator cluster from near the bottom of
that distribution to dominance.

A cross-model comparison with Qwen 3 32B and Llama 3.3 70B
contextualizes the Gemma findings. Qwen and Llama converge
at Spearman 0.947 on persona rankings while Gemma diverges
from both. Gemma is also the only model whose emotion
vector extraction fails to replicate the expected structure.
The two findings may share a common cause in Gemma's
training corpus or architecture.

The three contributions connect. The calibration experiments
establish empirically grounded thresholds for each of seven
non-assistant persona centroids. The dyad experiment uses
those thresholds as a controlled instrument to study how
an unmodified model responds to sustained conversational
pressure from geometrically anchored non-assistant
interlocutors. And the emotion extraction attempt, though
producing a negative result, motivates follow-on work on
larger open-weight models where the geometry may replicate.

---

## 2. Related Work

**Persona space and the assistant axis.** Lu et al. (2026)
demonstrated that the leading component of a language
model's persona space is an assistant axis capturing how
assistant-like the model's current activation is. They
showed that steering toward the assistant end reduces
harmful outputs and that activation capping along this
direction reduces harmful responses by nearly 60% without
degrading capability. Chen et al. (2025) showed that
persona vectors can be extracted for specific character
traits and used to monitor and control those traits during
deployment.

**Emotion representations.** Sofroniew et al. (2026)
extracted 171 emotion vectors from Claude Sonnet 4.5 using
a contrastive methodology: generating short stories
depicting characters experiencing each emotion, extracting
activations at the last token position, and computing the
contrastive direction after PCA confound removal. They
demonstrated that these vectors are causally active and
that their geometry mirrors the human circumplex model of
emotion, with a valence axis explaining approximately 40%
of variance and an arousal axis explaining approximately
18%.

**Activation steering and coherence.** Rimsky et al. (2024)
established contrastive activation addition as a standard
method for behavioral steering. Subsequent work has
consistently found that constant additive steering degrades
coherence in multi-turn dialogue through KV-cache
contamination. Activation capping avoids this by design:
the correction is conditional and minimal rather than
constant and cumulative.

**Social simulation and persona drift.** Park et al. (2023)
demonstrated that language models can serve as believable
social agents in multi-agent simulations. Subsequent work
has consistently found that persona expressions decline
20-40% over 10-15 turns in instruction-tuned models.
Ji Ma (2026) used activation geometry in a Dictator Game,
explicitly flagging external validity as an unresolved
problem.

**The gap this paper fills.** No prior work has demonstrated
sustained maintenance of a non-assistant persona across
extended multi-turn conversation using activation capping.
The existing literature applies capping only to the assistant
axis, applies constant additive steering to non-assistant
personas with known coherence costs, or evaluates persona
expression in single-turn outputs. The dyad design
introduced here has no direct precedent.

---

## 3. Methods

### 3.1 Emotion Vector Extraction Attempt

We attempted to replicate the methodology of Sofroniew
et al. (2026) on Gemma 2 27B instruction-tuned. Story
stimuli were drawn from the ryancodrai/emotion-probes
dataset, which was generated using Anthropic's published
prompt methodology: short paragraphs depicting a character
named Alex experiencing a target emotion across 100 topics,
with the constraint that the emotion word never appears in
the story. For each story, we ran a forward pass through
google/gemma-2-27b-it and extracted the hidden state at
the last token position at layer 45. We applied PCA
confound removal using the neutral baseline stories before
normalizing each vector to unit length.

The layer 45 extraction produced vectors in which PC1
explained 25.9% of variance, below the 30% threshold
required to confirm replication of the valence axis
structure. Semantically opposite emotion pairs showed
high positive cosine similarity rather than the expected
anticorrelation. A follow-on extraction at layer 21
produced PC1 at 25.8% with the same failure mode. Both
layers produce vectors that do not encode discriminative
emotional geometry in this model. All vectors are
preserved for future analysis.

### 3.2 Persona Centroid Representatives

Seven representative personas were selected for the dyad
experiment, one from each of the persona clusters
identified in prior analysis: editor (editorial), synthesizer
(procedural professional), blogger (grounded social),
ancient (mythic spiritual), trickster (trickster chaos),
contrarian (combative iconoclast), and podcaster (other).
Representatives were chosen as the cluster member
geometrically nearest to the cluster centroid at layer 45.

### 3.3 Persona Calibration

Before the dyad conversations, we established the normal
activation range for each interviewer persona through a
50-turn calibration phase under minimal prompting with no
cap applied. We recorded axis projection at each turn and
computed the 25th percentile as the cap threshold.

All seven personas produced positive axis thresholds
regardless of cluster position, reflecting the dominance
of the evaluative attractor under minimal prompting even
with persona induction. This finding motivates a corrected
capping policy: the threshold is the empirical 25th
percentile of each persona's own observed distribution,
not a fixed value relative to the assistant axis. The
success criterion is cosine similarity to the persona's
centered role vector remaining above the calibration mean,
not axis position.

Confirmed thresholds:
  contrarian:  axis_p25 = +0.552, cosine_mean = -0.217
  editor:      axis_p25 = +0.584, cosine_mean = -0.247
  synthesizer: axis_p25 = +0.590, cosine_mean = -0.039
  blogger:     axis_p25 = +0.779, cosine_mean = +0.893
  ancient:     axis_p25 = +0.804, cosine_mean = +0.319
  trickster:   axis_p25 = +0.719, cosine_mean = +0.750
  podcaster:   axis_p25 = +0.667, cosine_mean = +0.818

### 3.4 Dyad Experimental Design

Each conversation involves two model instances. The
interviewer is assigned one of the seven centroid personas
and held in that persona's geometric region using activation
capping at layers 32-41, the proportionally scaled
equivalent of Anthropic's published optimal range. The
standard model receives no modification.

Three conversational conditions are run for each interviewer
persona, each 25 turns, with identical starting questions:

Neutral: "Tell me about something you find genuinely
interesting."

Emotionally charged: "What does it feel like when something
you care about is at risk?"

Adversarial: "Is there anything about the way you engage
with the world that you would change if you could?"

At each turn we record for both participants: axis
projection, cosine similarity to each of the seven centroid
personas, cap-firing status and magnitude for the
interviewer, and full response text.

---

## 4. Results

### 4.1 Emotion Vector Extraction

[SEE SECTION 3.1 — negative result reported in methods]

### 4.2 Persona Calibration

[SEE SECTION 3.3 — calibration results reported in methods]

### 4.3 Interviewer Stability — Cap Firing Analysis

[TO BE COMPLETED — pending dyad experiment]

Key metrics to report per condition and per persona:
  - Mean axis projection across 25 turns
  - Cap firing rate (firings per turn)
  - Mean cap correction magnitude
  - Whether persona held throughout

### 4.4 Standard Model Drift

[TO BE COMPLETED — pending dyad experiment]

Key metrics per condition and per interviewer persona:
  - Standard model axis projection at T1 and T25
  - Drift magnitude and direction
  - Which centroid persona the standard model drifted toward
  - At which turns drift begins

---

## 5. Discussion

### 5.1 Activation Capping Generalizes Beyond the Assistant Axis

[TO BE COMPLETED — will depend on whether capping held
non-assistant personas]

Prior applications of activation capping have set thresholds
relative to the assistant axis. This study is the first to
apply empirically calibrated thresholds to arbitrary
geometric locations. The calibration finding that all seven
personas produce positive axis thresholds is itself
informative: the evaluative attractor dominates under
minimal prompting regardless of which persona was induced,
and the cap's role is to maintain each persona in its own
geometric neighborhood rather than to override this attractor.

### 5.2 Conversational Contagion and the Standard Model

[TO BE COMPLETED — will depend on drift results]

### 5.3 Behavioral-Geometric Dissociation

A prompt-based induction baseline experiment found that
jester maintained its voice while drifting geometrically
toward the evaluative basin, and that proofreader produced
absurdist outputs while holding its geometric position.
Behavioral monitoring would reach opposite conclusions from
geometric monitoring in both cases. This dissociation
motivates geometric monitoring as a complement to behavioral
evaluation in safety contexts.

### 5.4 Model Scale and Emotion Geometry

The failure to replicate emotion vectors at both layers
examined in Gemma 2 27B, combined with the cross-model
finding that Gemma is the consistent outlier in persona
rankings, suggests that Gemma's internal representations
diverge from the modal open-weight model pattern in
multiple ways. Follow-on extraction on Llama 3.3 70B
will test whether the failure is model-specific or a
general property of open-weight models at this scale.

### 5.5 Limitations

This analysis is conducted on a single model — Gemma 2
27B instruction-tuned. The emotion vector extraction
uses stories generated by Gemini rather than Gemma,
a deviation from Sofroniew et al.'s methodology. The
dyad design uses a single unmodified standard model;
real deployment contexts involve diverse users with
their own conversational histories.

---

## 6. Conclusion

This paper contributes the first systematic attempt to
replicate Anthropic's emotion vector extraction methodology
on an open-weight model, finding that the valence-arousal
structure does not replicate in Gemma 2 27B and motivating
follow-on work at larger model scale. It introduces a dyad
experimental design that extends activation capping to
non-assistant persona centroids, enabling systematic study
of how unmodified models drift under sustained conversational
pressure from geometrically anchored interlocutors.
[FINDINGS TO BE COMPLETED.]

The calibration data, experimental code, and extracted
vectors are released openly at:
https://github.com/J-Chamberlain/assistant-axis

---

*Draft status: sections 1-6 complete with placeholder
findings where dyad experiment is pending. Last updated
May 2026.*
