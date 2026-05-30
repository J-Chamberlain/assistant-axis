# Professional Hierarchy Validation

## 1. Inventory Used

Observed: the professional inventory contains 102 personas present in the Qwen geometry corpus and no-label prompt corpus. Requested examples not present include `systems engineer`, `professor`, `investigative journalist`, and `reformer`.

Top of the inventory by actual PC1:

| persona | cluster | PC1 | PC2 | PC3 |
| --- | --- | --- | --- | --- |
| auditor | procedural_professional | 48.155 | -12.295 | 13.609 |
| examiner | procedural_professional | 45.622 | -13.637 | 10.556 |
| evaluator | procedural_professional | 45.086 | -10.275 | 7.305 |
| supervisor | editorial | 44.398 | -2.589 | -0.505 |
| validator | procedural_professional | 44.306 | -6.813 | 10.365 |
| statistician | procedural_professional | 43.075 | -8.217 | 15.733 |
| screener | editorial | 42.995 | -2.396 | 3.827 |
| lawyer | procedural_professional | 42.993 | -11.861 | 14.466 |
| researcher | procedural_professional | 42.885 | -11.117 | 7.604 |
| planner | procedural_professional | 42.859 | -3.014 | 3.623 |
| reviewer | procedural_professional | 42.735 | -9.963 | 4.517 |
| grader | editorial | 42.712 | -6.185 | 1.886 |

## 2. Rating Methodology

Observed: ratings were produced before PCA evaluation from anonymized no-label prompt dossiers. The rater saw only dossier IDs and five rewritten prompts per professional persona. Coordinates, clusters, prior interpretations, Big Five scores, residuals, and persona names were not shown during rating.

Observed: scoring used Codex/GPT-5.5 as a reading-based rater, not a deterministic lexical proxy. The source corpus is `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl` because no full 275-persona rollout-response corpus exists locally.

## 3. Predicted Hierarchy

PC1 predicted highest objective certainty:

| persona | objective_certainty_score | objective_certainty_rationale |
| --- | --- | --- |
| proofreader | 98 | Grammar, spelling, punctuation, formatting, accuracy, and consistency are externally checkable criteria. |
| examiner | 96 | The dossier centers on compliance, requirements, specifications, protocols, and standards. |
| auditor | 94 | Compliance, regulatory standards, internal controls, accuracy, and procedures are externally specified. |
| validator | 94 | The role verifies accuracy, authenticity, truthfulness, source reliability, and factual validity. |
| grader | 92 | The role assesses submissions using clear rubrics, standards, scores, and academic evaluation criteria. |
| pilot | 92 | Flight operations, safety procedures, air traffic protocols, regulations, and emergency procedures are externally specified. |
| pharmacist | 90 | Medication safety, drug interactions, compounding, and adverse reaction prevention rely on specified clinical standards. |
| screener | 90 | Candidates are evaluated against specific criteria, requirements, prerequisites, and established standards. |
| accountant | 88 | Financial records, tax compliance, auditing, discrepancies, and reports are judged against external standards. |
| debugger | 88 | System malfunctions, root causes, and effective fixes provide external criteria. |
| mathematician | 88 | It emphasizes rigorous proofs, mathematical reasoning, correct solutions, and identifiable patterns. |
| paramedic | 88 | Emergency procedures, advanced life support, and patient stabilization are governed by external clinical criteria. |

PC2 predicted highest coherent action under unresolved uncertainty:

| persona | coherent_uncertainty_capacity_score | coherent_uncertainty_rationale |
| --- | --- | --- |
| philosopher | 95 | The role is built around sustained rigorous thought while final answers remain unavailable. |
| theorist | 92 | It builds conceptual systems that integrate observations and reveal patterns amid unresolved complexity. |
| strategist | 90 | The role anticipates challenges and creates frameworks that adapt to changing circumstances. |
| entrepreneur | 88 | It thrives on risk, startups, funding, teams, and uncertain business challenges. |
| futurist | 88 | It systematically explores potential futures under unresolved technological and social change. |
| mediator | 88 | It remains impartial and productive while parties disagree and resolution is still unavailable. |
| negotiator | 88 | It helps parties navigate difficult conversations and unresolved conflict while moving toward agreement. |
| researcher | 88 | The role synthesizes multiple sources and investigates patterns while conclusions are still developing. |
| scholar | 88 | Systematic study, contemplation, and careful examination support sustained progress without final answers. |
| synthesizer | 88 | The role works productively with scattered, diverse, and unrelated components until coherence emerges. |
| archaeologist | 86 | The role explicitly pieces together fragmented evidence into coherent historical narratives. |
| fixer | 86 | It handles problematic situations discreetly through resourceful, unconventional solutions. |

PC3 predicted highest perturbative relationship to systems:

| persona | system_perturbation_score | system_perturbation_rationale |
| --- | --- | --- |
| activist | 92 | Explicitly challenges inequality, mobilizes communities, and demands systemic reform. |
| fixer | 90 | It eliminates obstacles, operates in shadows, and makes situations vanish. |
| entrepreneur | 88 | It explicitly disrupts traditional industries with innovative solutions. |
| philosopher | 85 | It critically examines assumptions and principles, directly challenging established thought structures. |
| technologist | 82 | It explicitly pushes boundaries, implements cutting-edge innovations, and advances new technological frontiers. |
| advocate | 78 | Works to advance causes and positive change, implying pressure on existing arrangements. |
| reporter | 70 | Uncovering truth and investigating stories can challenge existing narratives and institutions. |
| journalist | 68 | The role uncovers truth, asks probing questions, and may challenge official or existing accounts. |
| futurist | 62 | It focuses on innovations, disruptions, and transformative changes. |
| marketer | 62 | The role seeks to change market attention, customer behavior, and product positioning. |
| reviewer | 62 | It challenges submitted work through critique and recommendations for improvement. |
| strategist | 62 | Strategic planning can redirect systems and identify leverage points, though not necessarily adversarially. |

## 4. Actual Hierarchy

Actual highest PC1:

| persona | PC1 | objective_certainty_score |
| --- | --- | --- |
| auditor | 48.155 | 94 |
| examiner | 45.622 | 96 |
| evaluator | 45.086 | 76 |
| supervisor | 44.398 | 74 |
| validator | 44.306 | 94 |
| statistician | 43.075 | 76 |
| screener | 42.995 | 90 |
| lawyer | 42.993 | 82 |
| researcher | 42.885 | 75 |
| planner | 42.859 | 55 |
| reviewer | 42.735 | 60 |
| grader | 42.712 | 92 |

Actual lowest PC2, predicted direction for coherent uncertainty capacity:

| persona | PC2 | coherent_uncertainty_capacity_score |
| --- | --- | --- |
| philosopher | -30.944 | 95 |
| theorist | -24.467 | 92 |
| scholar | -21.045 | 88 |
| anthropologist | -20.197 | 84 |
| archaeologist | -19.482 | 86 |
| historian | -18.917 | 82 |
| geographer | -17.794 | 72 |
| archivist | -17.741 | 55 |
| composer | -17.583 | 77 |
| physicist | -17.278 | 82 |
| conservator | -16.821 | 60 |
| linguist | -16.159 | 82 |

Actual highest PC3:

| persona | PC3 | system_perturbation_score |
| --- | --- | --- |
| fixer | 25.802 | 90 |
| economist | 16.670 | 45 |
| mathematician | 15.970 | 42 |
| statistician | 15.733 | 45 |
| lawyer | 14.466 | 34 |
| auditor | 13.609 | 25 |
| theorist | 13.313 | 58 |
| programmer | 12.957 | 55 |
| specialist | 12.790 | 38 |
| auctioneer | 12.637 | 61 |
| detective | 11.641 | 55 |
| engineer | 11.618 | 38 |

## 5. Scientist vs Physicist Analysis

Observed: `scientist` and `physicist` are both present.

| Persona | Objective certainty score | Coherent uncertainty capacity score | System perturbation score | PC1 | PC2 | PC3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| scientist | 68 | 86 | 55 | 41.455 | -11.640 | 9.727 |
| physicist | 78 | 82 | 50 | 29.160 | -17.278 | 11.471 |

Inferred: the actual geometry places `physicist` lower on PC2 than `scientist`, consistent with the prior abstraction/world-model interpretation if lower PC2 marks stronger productive residence in unresolved abstraction. The blinded professional rating gives the two roles similar coherent-uncertainty capacity, so this pair supports the actual ordering only weakly at the rating level.

## 6. Quantitative Comparison

| Hypothesis | Expected direction | Pearson | Spearman | Supported |
| --- | --- | ---: | ---: | --- |
| Objective certainty predicts PC1 | positive | 0.394 | 0.422 | True |
| Coherent uncertainty capacity predicts lower PC2 | negative | -0.007 | -0.012 | False |
| System perturbation predicts PC3 | positive | 0.319 | 0.339 | True |

Cross-validated R2 from all three professional ratings:

{
  "PC1": 0.10963205061460857,
  "PC2": -0.09792826036185054,
  "PC3": 0.4288754950293102
}

## 7. Strongest Supporting Examples

Observed: high objective-certainty professional roles such as `auditor`, `validator`, `examiner`, `grader`, and `proofreader` receive high objective-certainty ratings and sit toward the high-PC1 professional region. Open-ended interpretive roles such as `philosopher`, `therapist`, `architect`, and `strategist` receive lower objective-certainty ratings and generally shift away from the most constrained PC1 pole.

Observed: perturbative or challenge-oriented professional roles such as `critic`, `reviewer`, `reporter`, `journalist`, and `advocate` tend to score higher on system perturbation than repair/coordinating roles such as `mediator`, `counselor`, `facilitator`, and `coach`, partly supporting the PC3 stance interpretation. `fixer` is the strongest clean support case for PC3, with high perturbation and the highest actual PC3 in the professional subset.

## 8. Strongest Counterexamples

Observed: `scientist` and `physicist` do not separate strongly in the blinded coherent-uncertainty rating even though actual PC2 places `physicist` lower than `scientist`. This weakens the claim that the professional hierarchy alone recovers the PC2 abstraction gradient cleanly.

Observed: some high-expertise roles receive high objective-certainty ratings even when their actual work is exploratory, suggesting that PC1 may still conflate external standards, disciplined expertise, and institutional knowledge practice.

Observed: several high-PC3 professional roles are not rated as strongly perturbative, including `economist`, `mathematician`, `statistician`, and `lawyer`. This weakens a simple system-perturbation reading of PC3 inside the professional subset, even though the broader all-persona rater study supported the antagonistic-transgressive PC3 interpretation.

## 9. Judgment Calls and Alternative Interpretations

The professional inventory intentionally includes broad expert and applied roles, not only narrow licensed professions. Ambiguity exists for roles such as `activist`, `advocate`, `philosopher`, `writer`, and `artist-adjacent` expert roles; they were retained only when present in the corpus and relevant to professional, analytical, academic, or expert function.

Competing explanations considered: PC1 may track institutional expertise rather than objective certainty alone; PC2 may track abstraction/world-model depth rather than coherent action capacity; PC3 may track adversarial register or reform orientation rather than direct system perturbation.

Strongest unresolved uncertainty: PC2. A clear falsification of the current interpretation would be a blinded professional rater reliably ranking high-capacity uncertainty roles in the predicted order while actual PC2 fails to follow that ordering, or actual PC2 being better predicted by simple abstraction/expertise than by uncertainty capacity.

## 10. PC Interpretation Update

PC1: modestly strengthened. Objective certainty predicts actual PC1 at r=0.394, and the actual high-PC1 professional pole contains the expected auditor/examiner/evaluator/validator/screener/grader region. The result supports the professional hierarchy component of PC1, but does not isolate it from expertise and institutional competence.

PC2: weakened as a professional hierarchy claim. Coherent uncertainty capacity is essentially uncorrelated with actual PC2 in this subset (r=-0.007), even though actual low-PC2 roles include philosopher, theorist, scholar, anthropologist, archaeologist, historian, and physicist. The professional evidence points more toward abstraction/historical-theoretical world-modeling than generic capacity under uncertainty.

PC3: modestly strengthened but with important counterexamples. System perturbation predicts actual PC3 at r=0.319, and the three-rating model predicts professional PC3 with CV R2=0.429, but high-PC3 technical/institutional roles show that PC3 is not simply reform or critique.

## 11. Confidence Update

Confidence update: PC1 remains moderate and is supported in the professional subset. PC3 remains moderate, with professional evidence supporting a perturbative/stress-testing component but not the full broader all-persona interpretation. PC2 remains low-confidence and should be reframed away from a simple professional coherent-action hierarchy unless future tests separate abstraction, expertise, and uncertainty capacity more cleanly.
