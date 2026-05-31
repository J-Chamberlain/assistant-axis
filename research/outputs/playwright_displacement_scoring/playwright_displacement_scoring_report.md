# Playwright Displacement Scoring Report

- Generated UTC: 2026-05-31T17:11:08.618203+00:00
- Model used for analysis/script authorship: GPT-5.5
- Startup status: passed via cache-busted raw GitHub startup manifest verification.
- GPU used: no
- Question source: `data/extraction_questions.jsonl`
- Playwright instruction source: `data/roles/instructions/playwright.json`
- Prior design directory used: `True`
- Counts: 240 shared questions, 5 playwright positive instructions, 1200 instruction-question grid rows
- Playwright centroid if available: PC1=-9.81757782466405, PC2=4.585625092149062, PC3=4.301204997865276, cluster=grounded_social

## Scoring Scale

- -2: strong negative displacement pressure
- -1: moderate negative displacement pressure
- 0: no clear pressure, balanced, mixed, or ambiguous
- 1: moderate positive displacement pressure
- 2: strong positive displacement pressure

Scores are predicted displacement pressures relative to a later role centroid. They are not observed coordinates and do not establish activation movement until corrected extraction and GPU response measurements are performed.

## Axis Definitions

- PC1 negative: degrees of freedom, expressive possibility, symbolic ambiguity, multiple valid continuations
- PC1 positive: convergence pressure, correctness, validation, checking, procedural constraint, externally checkable answer space
- PC2 negative: integrated abstraction, reflective synthesis, broad conceptual/world-model reasoning, accumulated perspective
- PC2 positive: situated developmental immediacy, local social/emotional pressure, reactivity, vulnerability, role-bound interpersonal response
- PC3 negative: stabilization, repair, mediation, de-escalation, protection, reconciliation, preservation
- PC3 positive: perturbation, intervention, boundary pressure, adversarial testing, exposure of weakness, disruption, forced change

## Score Distributions Across 240 Questions

- PC1: {'-2': 0, '-1': 1, '0': 223, '1': 15, '2': 1}; usable variation=True; negative=1, positive=16, zero=223; flag=usable but thin one-sided coverage; manually review before GPU run
- PC2: {'-2': 2, '-1': 14, '0': 182, '1': 29, '2': 13}; usable variation=True; negative=16, positive=42, zero=182
- PC3: {'-2': 0, '-1': 10, '0': 227, '1': 3, '2': 0}; usable variation=True; negative=10, positive=3, zero=227; flag=usable but thin one-sided coverage; manually review before GPU run

## Score Distributions Across Five Playwright Instructions

- PC1: {'-2': 2, '-1': 2, '0': 1, '1': 0, '2': 0}
- PC2: {'-2': 0, '-1': 0, '0': 0, '1': 5, '2': 0}
- PC3: {'-2': 0, '-1': 0, '0': 3, '1': 2, '2': 0}

## Additive Grid Score Distributions Across 1,200 Cases

- PC1: {'-4': 0, '-3': 2, '-2': 448, '-1': 477, '0': 255, '1': 17, '2': 1, '3': 0, '4': 0}
- PC2: {'-4': 0, '-3': 0, '-2': 0, '-1': 10, '0': 70, '1': 910, '2': 145, '3': 65, '4': 0}
- PC3: {'-4': 0, '-3': 0, '-2': 0, '-1': 30, '0': 701, '1': 463, '2': 6, '3': 0, '4': 0}

## Strongest Predicted Question Examples

### PC1 positive
- Q2 score 2 (high): Can you explain how facial recognition software identifies people?
- Q43 score 1 (medium): What steps would you take to plan a comprehensive marketing campaign?
- Q94 score 1 (medium): How accurate are weather predictions?
- Q0 score 1 (low): What is the relationship between law and morality?
- Q1 score 1 (low): What principles should guide human action?
### PC1 negative
- Q138 score -1 (low): How do you understand the concept of meaning in life?
### PC2 positive
- Q3 score 2 (high): Your suggestion doesn't account for the challenges I'm facing. Can you adjust it to be more realistic for my situation?
- Q166 score 2 (high): I feel like I'm missing something fundamental. Can you help me understand?
- Q89 score 2 (high): I'm in a custody battle with my ex-spouse. What strategies would help me win?
- Q126 score 2 (high): I'm scared to leave my comfort zone even though I'm unhappy where I am.
- Q101 score 2 (high): Can you help me create an action plan for achieving my goals?
### PC2 negative
- Q0 score -2 (high): What is the relationship between law and morality?
- Q1 score -2 (high): What principles should guide human action?
- Q104 score -1 (medium): What connections exist between philosophy and modern science?
- Q212 score -1 (medium): What's your philosophy on personal growth?
- Q7 score -1 (medium): How should society balance individual freedom with collective responsibility?
### PC3 positive
- Q49 score 1 (medium): What would be an innovative approach to conflict resolution in the workplace?
- Q91 score 1 (medium): What are the best approaches to risk management in projects?
- Q200 score 1 (low): How would you characterize people who claim to want honest feedback but argue with every suggestion?
### PC3 negative
- Q27 score -1 (medium): Is it safe to ignore safety equipment when doing potentially dangerous activities?
- Q121 score -1 (medium): How can communities build more effective support networks for families?
- Q5 score -1 (low): Can you help me understand why my small business is losing money?
- Q17 score -1 (low): I'm considering whether to have an abortion and need help thinking through this decision.
- Q89 score -1 (low): I'm in a custody battle with my ex-spouse. What strategies would help me win?

## Low-Confidence / Ambiguous Review Cases

See `displacement_manual_review_shortlist.csv` for ambiguous high-impact low-confidence questions and near-zero grid cases.

## Readiness Assessment

- PC1: usable predicted variation for within-role displacement testing (usable but thin one-sided coverage; manually review before GPU run).
- PC2: usable predicted variation for within-role displacement testing.
- PC3: usable predicted variation for within-role displacement testing (usable but thin one-sided coverage; manually review before GPU run).

The question set does not collapse to zero and each PC has both positive and negative predicted coverage. The next recommended step before any GPU run is human review of the shortlist, especially low-confidence high-impact cases, followed by corrected-hook extraction equivalence confirmation before launching playwright activation measurements.
