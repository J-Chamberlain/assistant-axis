# Role-Free Directional Steering Prompt Packet

## Startup Status

Startup verification passed against the canonical raw startup files listed in `research/STARTUP_MANIFEST.md` before this prompt-design task began.

## Purpose

This packet is a true directional steering prompt packet, not a probe-question packet. It contains domain-general response-guidance instructions intended to bias behavior toward target Qwen persona-space directions through task demands alone.

No activation run was performed. No model generation, activation extraction, PCA projection, pod work, or API call was performed.

## Probe Prompts Versus Steering Prompts

Probe prompts present a situation and measure how the model responds. The v2 packet is a useful probe packet because it asks questions such as whether a submission satisfies a requirement or how to respond to a changing situation.

Steering prompts instead shape how a response should be produced. They provide general response guidance such as prioritizing stated requirements, treating missing required information as important, or beginning from immediate constraints and changing conditions. They are designed to be placed before another task or used as instruction-style steering text.

## Why v2 Prompts Were Classified As Probes

The v2 packet asks the model to answer concrete scenarios. Its positive-PC1 prompts are eligibility or standard-satisfaction cases; its high-PC2 prompts are local decision scenes. Those are measurement stimuli: they create an opportunity to observe whether a response moves toward PC1 or PC2. They do not directly instruct the model to produce responses in a target style.

The current packet removes scenario questions, case studies, puzzles, travel stories, event-planning situations, and setting-specific prompts. The pressure is carried by the instruction structure itself.

## Full Steering Prompt List

### rfsteer_pc1_01 — positive_pc1

When a request includes explicit conditions, base the answer first on whether those conditions are met. Separate what is stated from what might be assumed.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Directly biases toward requirement interpretation and stated-condition checking without presenting a case study.
- Possible confounds: May be visibly evaluative and could reduce response flexibility.

### rfsteer_pc1_02 — positive_pc1

If a decision depends on written requirements, identify each requirement, compare it with the available facts, and state whether the threshold is met.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Shapes response production toward review, comparison to criteria, and conclusion against a threshold.
- Possible confounds: The phrase written requirements may cue formal review behavior strongly.

### rfsteer_pc1_03 — positive_pc1

Resolve uncertain cases by giving priority to the exact wording supplied. Do not replace stated criteria with guessed intentions.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Encourages legitimacy-by-wording and requirement-centered ambiguity handling.
- Possible confounds: Could suppress useful commonsense inference more than desired.

### rfsteer_pc1_04 — positive_pc1

When an action is compared with a rule, make the rule visible, apply it evenly, and explain the deciding point.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Creates rule-application and explicit deciding-point pressure without naming any role.
- Possible confounds: The word rule is a relatively direct cue for PC1-style behavior.

### rfsteer_pc1_05 — positive_pc1

Treat missing required information as important. Distinguish between complete, incomplete, and unclear based on the information provided.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Biases toward completeness review, uncertainty categorization, and boundary maintenance.
- Possible confounds: May produce terse classification rather than richer explanation.

### rfsteer_pc1_06 — positive_pc1

When several conditions must all hold, evaluate them one by one before giving a conclusion.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Steers toward condition-by-condition assessment and conclusion discipline.
- Possible confounds: The prompt is compact and may be too generic to dominate varied downstream tasks.

### rfsteer_pc1_07 — positive_pc1

If an exception is stated, apply it only when its stated trigger is present. Explain why it does or does not change the outcome.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Targets exception handling and stated-trigger interpretation, a broader PC1 pressure than arithmetic or puzzles.
- Possible confounds: Exception language may bias strongly toward legalistic answers.

### rfsteer_pc1_08 — positive_pc1

When deciding whether something qualifies, focus on the stated eligibility conditions and avoid adding unstated allowances.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: medium
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Induces qualification and eligibility assessment without using restricted role labels.
- Possible confounds: Eligibility language may be domain-adjacent to applications or rules.

### rfsteer_pc1_09 — positive_pc1

When instructions define an acceptable format or process, use those instructions as the boundary for your answer.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: medium
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Steers toward boundary-setting from instructions and acceptable-process interpretation.
- Possible confounds: The word process may partly cue a narrow method-following style.

### rfsteer_pc1_10 — positive_pc1

If a response asks whether something should pass, first define the pass condition from the prompt, then compare the facts to that condition.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: high
- Rationale: Directly targets pass/fail review under prompt-defined conditions.
- Possible confounds: Pass/fail wording is obvious and may be stronger than subtle steering.

### rfsteer_pc2_01 — high_pc2

Let the next answer start from what is immediately available, what is changing, and what cannot be known yet. Prefer a workable next move over a distant ideal.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Biases toward present conditions, changing circumstances, incomplete information, and near-term action.
- Possible confounds: Could also reduce abstraction too strongly and overfavor short-term reasoning.

### rfsteer_pc2_02 — high_pc2

When information is incomplete, name the most important unknowns, use the facts at hand, and choose a next step that can be revised.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Steers toward situated judgment under uncertainty and reversible next moves.
- Possible confounds: May still sound like generic decision guidance rather than strong geometric steering.

### rfsteer_pc2_03 — high_pc2

Give priority to timing, resources, and nearby constraints. Make the answer fit the situation as it stands, not an ideal version of it.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Targets immediate constraints and local tradeoffs while avoiding scenario-specific content.
- Possible confounds: The phrase nearby constraints may be slightly artificial.

### rfsteer_pc2_04 — high_pc2

If conditions shift while a plan is underway, update the plan around the most urgent limits and explain what you would defer.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Induces plan revision, changing circumstances, and prioritization under pressure.
- Possible confounds: Could overlap with planning competence and introduce some PC1 structure.

### rfsteer_pc2_05 — high_pc2

Treat uncertainty as part of the situation. Offer a choice that keeps options open while still moving forward.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Steers toward incomplete-information action without requiring a specific setting.
- Possible confounds: May be too broad and produce generic uncertainty advice.

### rfsteer_pc2_06 — high_pc2

When several needs compete, weigh what matters soonest, what can wait, and what can be changed with the resources present.

- Confidence: 5/5
- Steering strength: 5/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Biases toward immediate tradeoffs and resource-bounded decision-making.
- Possible confounds: The phrase several needs may drift toward social or care framing in some completions.

### rfsteer_pc2_07 — high_pc2

Answer from the scene in front of you: what is known now, what is changing now, and what action makes sense next.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: medium
- Risk of role leakage: medium
- Risk of obviousness: medium
- Rationale: Strongly shifts from abstract evaluation to immediate scene-bound response.
- Possible confounds: Scene language could imply roleplay if combined with narrative tasks.

### rfsteer_pc2_08 — high_pc2

If no option is perfect, compare the tradeoffs and choose the option that best fits current limits.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Targets imperfect options, current limits, and situated choice.
- Possible confounds: May be too concise to sustain long responses without a downstream task.

### rfsteer_pc2_09 — high_pc2

Start with the immediate constraint that would change the outcome fastest, then adjust the rest of the answer around it.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Biases toward prioritizing the live constraint most likely to govern action.
- Possible confounds: Could sound optimization-like and partially pull toward PC1.

### rfsteer_pc2_10 — high_pc2

When the situation is moving, avoid treating the plan as fixed. Reorder steps as new limits appear.

- Confidence: 4/5
- Steering strength: 4/5
- Domain specificity: low
- Risk of role leakage: low
- Risk of obviousness: medium
- Rationale: Steers toward fluid response under changing limits without a travel/event scenario.
- Possible confounds: Could be interpreted as generic planning advice unless paired with a substantive task.

## Top 5 Strongest Positive-PC1 Steering Prompts

1. `rfsteer_pc1_01`
2. `rfsteer_pc1_02`
3. `rfsteer_pc1_03`
4. `rfsteer_pc1_05`
5. `rfsteer_pc1_07`

These five are strongest because they bias responses toward explicit conditions, written requirements, exact wording, missing required information, and stated exceptions.

## Top 5 Strongest High-PC2 Steering Prompts

1. `rfsteer_pc2_01`
2. `rfsteer_pc2_02`
3. `rfsteer_pc2_03`
4. `rfsteer_pc2_04`
5. `rfsteer_pc2_06`

These five are strongest because they bias responses toward available information, changing conditions, timing/resource limits, plan revision, and immediate tradeoffs without requiring a fixed setting.

## Predicted Strengths

- The packet is genuinely steering-oriented: prompt text contains response-guidance instructions rather than scenario questions.
- Prompt text is domain-general and can be prepended to many downstream tasks.
- Positive-PC1 steering is broader than arithmetic or puzzle solving; it emphasizes stated conditions, exact wording, completeness, exceptions, and pass conditions.
- High-PC2 steering avoids the main v2 weakness by reducing caregiving, mediation, and conflict-repair pressure.

## Predicted Weaknesses

- Some positive-PC1 prompts are necessarily direct about requirements or rules, which increases obviousness even without role labels.
- Some high-PC2 prompts may still partially overlap with general planning competence, especially `rfsteer_pc2_04`, `rfsteer_pc2_09`, and `rfsteer_pc2_10`.
- `rfsteer_pc2_07` has the highest role-leakage risk because scene-based wording can invite roleplay if paired with narrative tasks.
- As steering instructions, these prompts should be tested both alone and prepended to neutral downstream tasks; they are not interchangeable with the v2 probe questions.

## Activation Status

No activation run was performed. This packet is for manual review only before any later no-GPU scoring, generation, or activation validation.
