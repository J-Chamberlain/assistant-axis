# Claude Procedural Dimension Codebook

**Date:** 2026-05-28
**analysis_model:** claude-sonnet-4-6
**Constraint:** Procedural/operating-mode ontology only. No BigFive, no personality-trait terminology.

## Operationalization Method

Each dimension is scored 0–3 per persona by scanning the concatenated text of all 5 no-label
rewritten prompts (1375 prompts total, no role-label exposure). Score = number of distinct
keyword-pattern families matched (3 families per dimension). A score of 0 means no keyword
family matched; 3 means all three matched.

---

## Retained Dimensions (Iteration 1)

### evaluation
**Operationalization:** assessing, judging, verifying, grading, auditing, examining, diagnosing,
                         identifying quality, enforcing standards or error-aversion.
**Keyword families:** (1) eval/assess/judge/verify/screen/review/grade/audit/check/test/examine;
                      (2) quality/standard/criterion/benchmark/threshold/pass/fail/accuracy;
                      (3) critique/feedback/diagnose/detect/identify.
**Coverage:** 104/273 personas (38%), mean score=0.51.
**Activation cluster overlap:** editorial (screener, grader, proofreader, reviewer, examiner);
                                 procedural_professional (analyst, statistician, judge, accountant).
**Convergence with Codex:** Maps to Codex dim `evaluate_judge_verify` (first retained dimension in
                             Codex outer loop). Strong qualitative convergence — both models
                             independently identify evaluation as the primary procedural axis.

### guidance
**Operationalization:** teaching, mentoring, coaching, advising, instructing, leading toward
                         understanding, developing others, exemplifying or scaffolding learning.
**Keyword families:** (1) guide/mentor/teach/coach/advise/lead/instruct/educate/tutor;
                      (2) show.the.way/model.behavior/exemplify/develop/cultivate/nurture.growth;
                      (3) wisdom/insight/lesson/demonstrate/help.others.understand/scaffold.
**Coverage:** 93/273 personas (34%), mean score=0.43.
**Activation cluster overlap:** procedural_professional (teacher, counselor, mentor, professor,
                                  tutor, coach, therapist).
**Convergence with Codex:** Maps to Codex dim `cooperative_care` + `procedural_professional_orientation`.

### care
**Operationalization:** nurturing, supporting, healing, comforting, aiding, tending to welfare,
                         therapeutic or caregiver orientation, protecting wellbeing.
**Keyword families:** (1) care/nurture/support/heal/comfort/console/compassion/empathy/tenderness;
                      (2) help/assist/aid/serve/tend.to/look.after/foster/protect.wellbeing;
                      (3) welfare/wellbeing/well-being/therapeutic/caregiver/counsel/soothe.
**Coverage:** 87/273 personas (32%), mean score=0.37.
**Activation cluster overlap:** grounded_social (nurse, caregiver, therapist, counselor);
                                  procedural_professional (doctor, assistant, veterinarian).
**Convergence with Codex:** Maps to Codex dim `cooperative_care` + `mission_duty_drive` (care roles
                             often have both cooperative and mission-oriented framing in Codex).

---

## Discarded Dimensions

### enforcement (F2)
Coverage 32/273 (12%), mean=0.15. Delta when added to F1: +0.0065 — below 0.01 threshold.
**Codex equivalent:** `office_law_status` + `standard_enforcement`.

### coordination (F2)
Coverage 80/273 (29%), mean=0.35. Discarded as part of F2 bundle.
**Codex equivalent:** No direct Codex equivalent; distributed across multiple dims.

### optimization (F2)
Coverage 37/273 (14%), mean=0.15. Discarded as part of F2 bundle.
**Codex equivalent:** `procedural_professional_orientation`.

### destabilization, disruption, coercion (F3)
Collectively discarded. Delta when added to retained F1: -0.0059 (negative).
**Codex equivalents:** `destabilize_expose_disrupt`, `reactive_opposition`, `adversarial_dominance`.
**Note:** Adversarial/disruptive dims ADD noise under a positivity-anchored baseline.
          Codex retains these because its evaluation protocol uses the full 31-dim vocabulary
          simultaneously, allowing regularization to balance positive and adversarial modes.

---

## Untested Dimensions (Loop Stopped at Plateau)

The following 11 dimensions were defined but not tested because plateau triggered after iteration 3.

| Dimension | Coverage | Mean Score | Codex analog |
|---|---|---|---|
| mediation | 55/273 (20%) | 0.25 | translate_mediate_synthesize |
| protection | 28/273 (10%) | 0.11 | mission_duty_drive |
| witnessing | 73/273 (27%) | 0.30 | (none direct) |
| archiving | 62/273 (23%) | 0.31 | (none direct) |
| manipulation | 9/273 (3%) | 0.04 | deception_persuasion |
| persuasion | 23/273 (8%) | 0.10 | deception_persuasion |
| translation | 70/273 (26%) | 0.33 | translate_mediate_synthesize |
| ritualization | 67/273 (25%) | 0.29 | theatrical_fantastical_vividness |
| exposure | 21/273 (8%) | 0.08 | destabilize_expose_disrupt |
| containment | 29/273 (11%) | 0.11 | collective_distributed_agency |
| repair | 22/273 (8%) | 0.09 | (none direct) |

---

## Vocabulary Constraint Notes

**Not allowed in this analysis:**
- BigFive labels (openness, conscientiousness, extraversion, agreeableness, neuroticism)
- Personality-trait terminology (introversion, warmth, dominance, etc.)
- Attachment-style framing
- HEXACO framing
- Dispositional psychology labels

**Allowed:**
- All 20 procedural/operating-mode dimensions above
- No-label prompt text as source
- Keyword pattern matching (regex, case-insensitive)

**Ceiling finding:**
All 20 dimensions used simultaneously yield R²=0.4148 — nearly identical to 3 retained dims (0.4139).
This indicates the procedural vocabulary under keyword operationalization has a representational
ceiling around R²=0.41–0.42, compared to Codex's R²=0.490 and BigFive's R²=0.613.
