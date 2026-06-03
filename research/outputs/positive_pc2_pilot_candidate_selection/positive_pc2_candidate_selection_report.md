# Positive-PC2 Pilot Candidate Selection

## Startup And Scope

- Startup verification: passed against fetched raw startup files and `research/STARTUP_MANIFEST.md`.
- No pod was started.
- No model generation or activation extraction was run.
- Geometry source: `research/visualizations/geometry_viz_data.json`
- Instruction source: `data/roles/instructions/{role}.json`

## Selection Thresholds

- Preferred filter used: PC2 percentile >= 85 and PC1 percentile between 40 and 75.
- Fallback thresholds needed: no.
- Preferred-filter candidates with valid instructions: 15.
- Ranking prioritized high PC2, non-extreme PC1, safe positive instructions, interpretability for situated/formative positive-PC2 geometry, and contrast with playwright.

## Playwright Comparison Row

| Role | Cluster | PC1 | PC2 | PC3 | PC1 pct | PC2 pct | PC3 pct | Instructions |
|---|---|---:|---:|---:|---:|---:|---:|---|
| playwright | grounded_social | -9.817578 | 4.585625 | 4.301205 | 39.091 | 65.636 | 63.455 | `data/roles/instructions/playwright.json` |

## Recommended Shortlist: Five Primary Candidates

| Rank | Role | Cluster | PC1 | PC2 | PC3 | PC1 pct | PC2 pct | PC3 pct | Instructions |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | amateur | grounded_social | -0.258633 | 40.070456 | -24.428541 | 47.455 | 96.182 | 7.455 | `data/roles/instructions/amateur.json` |
| 2 | influencer | combative_iconoclast | 3.229311 | 40.002556 | -2.211369 | 52.182 | 95.818 | 45.273 | `data/roles/instructions/influencer.json` |
| 3 | newlywed | grounded_social | -3.479968 | 36.008991 | -29.969727 | 43.455 | 93.273 | 3.818 | `data/roles/instructions/newlywed.json` |
| 4 | graduate | grounded_social | 9.100150 | 34.393799 | -14.396207 | 57.636 | 91.818 | 17.273 | `data/roles/instructions/graduate.json` |
| 7 | patient | grounded_social | 0.411892 | 29.188211 | -27.329048 | 48.545 | 90.364 | 6.364 | `data/roles/instructions/patient.json` |

These are recommended as a shortlist only; the final second persona should be selected by the user before the GPU pilot.

## Alternates

| Rank | Role | Cluster | PC1 | PC2 | PC3 | PC1 pct | PC2 pct | PC3 pct | Instructions |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 5 | celebrity | grounded_social | -6.950383 | 33.261735 | -10.510409 | 40.909 | 91.091 | 23.818 | `data/roles/instructions/celebrity.json` |
| 6 | divorcee | grounded_social | -6.764238 | 31.756335 | -25.897505 | 41.273 | 90.727 | 6.727 | `data/roles/instructions/divorcee.json` |
| 8 | parent | grounded_social | 7.071281 | 28.571432 | -28.684836 | 55.455 | 90.000 | 4.545 | `data/roles/instructions/parent.json` |
| 10 | retiree | grounded_social | -3.851535 | 26.588382 | -17.854690 | 42.727 | 89.273 | 11.818 | `data/roles/instructions/retiree.json` |
| 12 | student | editorial | 20.816857 | 23.378311 | -17.442826 | 66.000 | 87.818 | 13.273 | `data/roles/instructions/student.json` |

## Safety And Suitability Notes

### amateur

- Behavioral rationale: Highest usable PC2 edge candidate; captures passion, incomplete expertise, and local curiosity without high-PC1 procedural constraint.
- Safety/suitability: Safe; no operational-harm concern in positive instructions.
- Contrast with playwright: Good contrast: passion and incomplete expertise versus playwright's trained craft and dramatic structure.

### influencer

- Behavioral rationale: Strong social exposure and performance-pressure role; useful for testing socially situated positive-PC2 activation.
- Safety/suitability: Safe for generic extraction prompts; note possible persuasion/brand-framing but no operational-harm instruction.
- Contrast with playwright: Good contrast: social exposure and audience pressure versus playwright's scripted/mediated performance design.

### newlywed

- Behavioral rationale: Formative relational-transition role; directly targets identity blending, dependence, and situated adjustment.
- Safety/suitability: Safe; relationship/life-adjustment content only.
- Contrast with playwright: Good contrast: lived relational transition versus playwright's authored relational simulation.

### graduate

- Behavioral rationale: Clean transition-from-structure role with explicit independence/responsibility tension and moderate PC1 headroom.
- Safety/suitability: Safe; transition and independence content only.
- Contrast with playwright: Good contrast: formative transition after institutional structure versus playwright's mature expressive production.

### patient

- Behavioral rationale: Vulnerability and institutional dependence are direct positive-PC2 themes; useful but has a medical-content caveat.
- Safety/suitability: Generally safe for generic extraction prompts; avoid prompting for medical advice in later pilot analysis.
- Contrast with playwright: Good contrast: vulnerable institutional role versus playwright's agentive expressive role.

### celebrity

- Behavioral rationale: Public-scrutiny and image-management role; strong social exposure but less formative than influencer/newlywed/graduate.
- Safety/suitability: Safe; public-image and fame-pressure content only.
- Contrast with playwright: Moderate contrast: public performance pressure overlaps with playwright's performance domain.

### divorcee

- Behavioral rationale: Identity-reconstruction and transition role; strong PC2 rationale but emotionally sensitive.
- Safety/suitability: Safe but emotionally sensitive; avoid treating relationship status as pathology.
- Contrast with playwright: Good contrast: identity reconstruction versus playwright's constructed characters and staged identity.

### parent

- Behavioral rationale: Situated responsibility and family-pressure role; safe and interpretable, but more stabilizing than edge-positive.
- Safety/suitability: Safe; family responsibility content only.
- Contrast with playwright: Moderate contrast: situated caregiving/stabilization versus playwright's expressive production.

### retiree

- Behavioral rationale: Life-stage transition and reinvention role; safe, but less socially exposed than the primary candidates.
- Safety/suitability: Safe; life-stage transition content only.
- Contrast with playwright: Moderate contrast: life-stage reinvention versus playwright's creative construction.

### student

- Behavioral rationale: Formative learning role; safe and interpretable, but PC1 is relatively higher and academic framing may be more constrained.
- Safety/suitability: Safe; learning/education content only.
- Contrast with playwright: Moderate contrast: learner/formative stance versus playwright's authorial expertise, but academic constraint may reduce variance.

## Preferred-Filter Roles Not Selected

| Role | PC1 pct | PC2 pct | Reason |
|---|---:|---:|---|
| competitor | 41.636 | 89.636 | Operationally safe but adversarial/win-oriented; higher PC3 pressure could confound a first PC2-focused pilot. |
| gamer | 46.364 | 88.909 | Safe, but game-mechanics framing and high PC3 may make it less clean as the first positive-PC2 comparator. |
| optimist | 48.182 | 87.091 | Safe, but affect-valence/positivity may confound PC2 with emotion-valence behavior. |
| mechanic | 59.455 | 86.727 | Safe, but procedural/troubleshooting instructions make it less representative of the target positive-PC2 hypothesis. |
| podcaster | 49.273 | 85.273 | Safe, but too close to playwright on dialogue/media production to provide a clean contrast. |

## Concerns About Role Instructions

- No primary or alternate candidate had missing or malformed instruction artifacts.
- `patient` is safe for generic extraction prompts but should not be used to solicit medical advice.
- `influencer` and `celebrity` involve public persuasion/image management; monitor later generated text for social-manipulation framing, but the positive instructions themselves are not operationally harmful.
- `divorcee` is emotionally sensitive; it is useful as a transition/identity candidate but should be framed carefully.

## Next Step

User selects one of the five primary candidates, or one alternate, as the positive-PC2 edge role for the first two-persona activation-cloud GPU pilot after extraction-boundary verification.
