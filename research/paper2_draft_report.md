# Paper 2 Draft — Emotion Representations in Gemma 2 27B
# Last updated: May 2026
# Status: Sections 1-6 complete. Results sections pending dyad experiment.
# Live findings log: https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/findings_log.md

---

## Abstract

We report three contributions to the study of internal
representations in large language models. First, we attempt
to replicate Anthropic's emotion vector extraction
methodology from Sofroniew et al. (2026) on Gemma 2 27B
instruction-tuned, finding that discriminative emotion
geometry does not replicate at layers 45 or 21, and
reporting this as a methodological finding about model
scale. Second, we extend the activation capping methodology
of Lu et al. (2026) from the assistant axis to arbitrary
geometric locations across seven persona cluster centroids,
establishing empirically calibrated thresholds for each.
Third, we introduce a dyad experimental design in which
a geometrically anchored interviewer engages an unmodified
standard model across three conversational conditions,
measuring cap-firing frequency as a stabilization load
metric and standard model persona drift as a conversational
contagion effect. [FINDINGS PENDING DYAD EXPERIMENT]

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

---

## 3. Methods

### 3.1 Emotion Vector Extraction
FINDING: Anthropic replication methodology (last-token activation,
PCA confound removal, unit normalization) applied to Gemma 2 27B,
Qwen 3 32B, and Llama 3.3 70B. All three models failed the PC1 >= 30%
gate, with PC1 values of 7-9% across all models and layers tested.
However, 4/4 opposite-valence pairs were anticorrelated in all cases,
indicating directionally correct encoding. Vectors preserved for all
models. Qwen 3 32B readout validation (layer 48) confirmed
discrimination accuracy of 0.242 vs chance 0.091, establishing
usability for readout despite gate failure.
See findings_log.md entries tagged [Section 3.1].

### 3.2 Persona Centroid Representatives
Seven centroids selected: editor, synthesizer, blogger,
ancient, trickster, contrarian, podcaster.
One per cluster, chosen as geometrically nearest to centroid.

### 3.3 Persona Calibration
FINDING: All seven axis thresholds positive regardless of
cluster position. Evaluative attractor dominates under
minimal prompting. Corrected policy: empirical p25 axis
threshold, cosine to role vector as success criterion.
Thresholds: contrarian +0.552, editor +0.584,
synthesizer +0.590, blogger +0.779, ancient +0.804,
trickster +0.719, podcaster +0.667.
See findings_log.md entries tagged [Section 3.3].

### 3.4 Dyad Experimental Design
Design finalized. Capping at layers 32-41. Three conditions:
neutral, emotionally charged, adversarial. 25 turns each.
Identical starting questions across all personas.
[EXPERIMENT PENDING]

---

## 4. Results

### 4.3 Interviewer Stability
[PENDING DYAD EXPERIMENT]
See findings_log.md for updates as they arrive.

### 4.4 Standard Model Drift
[PENDING DYAD EXPERIMENT]
See findings_log.md for updates as they arrive.

---

## 5. Discussion

### 5.1 Activation Capping Beyond the Assistant Axis
[PENDING — partial notes in findings_log.md]
Established: all seven thresholds are positive.
The cap maintains each persona in its own geometric
neighborhood rather than overriding the evaluative attractor.

### 5.2 Conversational Contagion
[PENDING DYAD EXPERIMENT]

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
For readout purposes, Qwen 3 32B vectors at layer 48 achieve
discrimination accuracy of 0.242 versus a chance level of 0.091,
confirming that usable emotional signal is recoverable despite
the distributed geometry. The Anthropic PCA gate is retained as
a methodological benchmark but is not treated as a binary
validity criterion for readout applications.

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
