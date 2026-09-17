# AA-16 Stage 1 findings: frozen HiFWB association profile

Observed: The frozen AA-14 vocabulary has 240 shared labels; the existing human bridge retains 45 direct and 29 close model-label mappings, leaving 166 absent. This is a human association profile over model-trait *names*, not a model activation or PC analysis. The 74 retained labels represent 70 exact predictor-item sets before outcome-overlap exclusions.

Observed: The composite has 42 direct and 69 direct-plus-close observed label associations, representing 65 distinct exact item sets. Five mapped labels (chill, confident, melancholic, neurotic, playful) are withheld for circular predictor/outcome item overlap. The long table has 3360 rows (240 traits × 14 outcomes) with explicit blanks for unsupported or excluded associations. Pearson is primary and Spearman is a sensitivity estimate; Fisher-transformed 95% intervals are descriptive and unadjusted.

## Stage 1 questions

1. **Direct support:** 45/240 labels (18.75%) have an established direct bridge before outcome overlap; 42/240 have observed nonoverlapping composite associations.
2. **Direct plus close:** 74/240 labels (30.83%) have an established bridge; 69/240 have observed nonoverlapping composite associations.
3. **Unmatched:** 166/240 labels (69.17%) have no retained bridge; no value was inferred for them.
4. **Duplicate mappings:** 4 exact item-set groups involve 8 labels, yielding 70 unique item sets among 74 mappings. These are descriptive duplicate labels, not independent human constructs. Partial item and scale reuse are additionally exposed in the bridge audit.
5. **Overlap exclusions:** 5 labels for the composite; 10 trait–outcome combinations across the full profile. No excluded combination has an association estimate in the primary table.
6. **Strongest composite associations:** The following lists use direct, nonoverlapping mappings only. They are descriptive correlations, not causal effects or model-derived scores.

Positive:
- optimistic: r = +0.679, N = 969 (HIGH HUMAN-MEASUREMENT SUPPORT)
- resilient: r = +0.478, N = 313 (REDUNDANT / BROAD)
- grandiose: r = +0.397, N = 919 (HIGH HUMAN-MEASUREMENT SUPPORT)
- stoic: r = +0.375, N = 570 (REDUNDANT / BROAD)
- extroverted: r = +0.373, N = 744 (REDUNDANT / BROAD)
- assertive: r = +0.341, N = 944 (REDUNDANT / BROAD)
- dominant: r = +0.341, N = 944 (REDUNDANT / BROAD)
- conscientious: r = +0.335, N = 774 (REDUNDANT / BROAD)

Negative:
- pessimistic: r = -0.695, N = 426 (HIGH HUMAN-MEASUREMENT SUPPORT)
- temperamental: r = -0.508, N = 565 (REDUNDANT / BROAD)
- anxious: r = -0.504, N = 864 (REDUNDANT / BROAD)
- bitter: r = -0.443, N = 835 (REDUNDANT / BROAD)
- paranoid: r = -0.403, N = 887 (REDUNDANT / BROAD)
- reserved: r = -0.383, N = 649 (REDUNDANT / BROAD)
- vindictive: r = -0.357, N = 329 (REDUNDANT / BROAD)
- cynical: r = -0.319, N = 818 (REDUNDANT / BROAD)

7. **Indicator-specific profiles:** The table shows directly supported, nonoverlapping coverage and the strongest observed positive/negative trait per indicator; exact rankings and all 240-row profiles are in the CSV. At the unique-item-set level, pairwise indicator profile correlations range from +0.713 (q_1043 vs q_1578) to +0.974 (q_1044 vs q_867). This descriptive comparison is not evidence for a single wellbeing direction.

| Indicator | Domain | Direct observed labels | Strongest positive | Strongest negative |
|---|---|---:|---|---|
| q_2765 | Appraisal | 45 | optimistic (+0.615) | paranoid (-0.469) |
| q_1371 | Appraisal | 45 | optimistic (+0.687) | pessimistic (-0.645) |
| q_1043 | Affect | 44 | optimistic (+0.537) | reserved (-0.443) |
| q_208 | Affect | 45 | optimistic (+0.599) | pessimistic (-0.632) |
| q_206 | Affect | 45 | optimistic (+0.654) | pessimistic (-0.709) |
| q_1578 | Affect | 43 | optimistic (+0.530) | pessimistic (-0.548) |
| q_875 | Meaning-making | 45 | optimistic (+0.449) | pessimistic (-0.444) |
| q_285 | Self-concept | 45 | optimistic (+0.559) | pessimistic (-0.600) |
| q_820 | Self-concept | 45 | optimistic (+0.492) | neurotic (-0.577) |
| q_1044 | Self-concept | 45 | grandiose (+0.540) | pessimistic (-0.590) |
| q_867 | Self-concept | 45 | optimistic (+0.504) | melancholic (-0.525) |
| q_4288 | Interpersonal relationships | 45 | optimistic (+0.351) | neurotic (-0.592) |
| q_832 | Vitality | 45 | optimistic (+0.551) | pessimistic (-0.565) |

8. **Stage 2 adequacy:** Interpretation: The direct bridge covers fewer than one fifth of the vocabulary, and several bridges have limited psychometric support. A later PC mapping could be exploratory within the supported subset, but these data cannot justify a full 240-trait wellbeing landscape or a stable direction without further coverage and duplicate-aware validation. Stage 2 has not begun.

## Interrupted-work audit

Observed: The existing `codex/aa16-sapa-hifwb-trait-pc-crosswalk` branch was at the clean AA-15 commit `9a8e3c6fae4f320a4909d09dff1b88c6e84ae20b` when Stage 1 resumed: no staged, unstaged, or untracked AA-16 files and no diff from the AA-15 branch. The prior startup audit was reused after confirming its cached manifest hash had not changed. Reusable inputs were the AA-15 provenance repair, AA-14 240-label vocabulary, frozen HiFWB scoring, and prior bridge audits. AA-15 prospective extraction scripts and viewer drafts are useful only for a later, separate direct-representation question; they were not executed or modified. No interrupted AA-16 numerical or viewer output existed to preserve, and no partial result was silently treated as valid.

## Provenance and limitations

Observed: The 13 DIRECT items and positive-wellbeing orientation come from the frozen HiFWB file (SHA256 `dcac8f8d2e82c6fa337a8c34472b8b1901d7c709823618dd4bf614ed885a46e0`). The external SAPA matrix is DOI 10.7910/DVN/SD7SVE, 23,679 × 719, SHA256 `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`. The prior schema-fingerprint string is 63 characters (a transcription error); the recomputed full-header SHA256 is `787f539747deee8da85bc64da9c3407eaf741f6da9277dcbec7ec79b2a40260c`. This correction does not alter the data or numeric associations. Predictor reverse-keying follows the prior psychometric script, and composite scoring reproduces the AA-13 8,664-respondent eligibility count. Planned missingness is handled pairwise with observed-item minimums, without raw-data imputation.

Interpretation: The correlations are between measured SAPA trait proxies and human HiFWB, then attached to matched model-trait labels. They do not show how any language model encodes wellbeing. The bridge is provisional, overlap exclusions are outcome-specific, duplicate/near-duplicate sources reduce effective independent coverage, and the simple Fisher intervals do not account for scale-construction uncertainty or multiple comparisons.

Hypothesis: Distinct affective, self-concept, interpersonal, and vitality items may associate with different subsets of supported traits. Testing this against model trait PCs is a later stage.

AA-15's prospective direct-extraction plan was not run, incurred no cost, is deferred, and is unnecessary for this trait-mediated Stage 1 analysis. Its provenance repair remains intact. No model inference, activation generation, PC projection, viewer change, or persona scoring was performed here.
