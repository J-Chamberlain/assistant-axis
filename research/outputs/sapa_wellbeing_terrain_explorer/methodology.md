# AA-12 SAPA Human Wellbeing Terrain Explorer — frozen methodology

This is a human-only, aggregate visualization over the frozen AA-10 SAPA V5 scoring definitions. The source is the 23,679-row SAPA V5 respondent matrix (local/gitignored); no respondent-level outputs are committed.

## Frozen choices

- Big Five coordinates: AA-10 `superKey696.csv` item membership and keyed signs; item scores are observed-only z scores and domain scores are means over at least two observed items, then standardized within the eligible five-domain cohort.
- Wellbeing outcomes: historical 13-item direct score (minimum 2 observed items), content-balanced score over Affect, Appraisal, Meaning-making, Self-concept, and Interpersonal relationships (minimum 2 or 3 content groups), non-affect direct score, vitality auxiliary score, and each content component. Community is not represented because the frozen SAPA mapping has no clean indicator.
- Empirical landscape: aggregate valid respondents into a deterministic 24×24 XY grid. Cells require at least 10 respondents for committed display; the surface value is the observed mean centered on the selected outcome cohort, with SD and SE retained.
- Conditional landscape: five-coordinate Ridge (alphas 0.1, 1, 10, 100 selected by 5-fold model-only CV) fit separately for each outcome using only human rows; hidden sliders are evaluated in standardized Big Five units. This is predictive, not causal.
- Support: standardized five-dimensional k-nearest-neighbor distance with k=10, converted to a percentile against the observed cohort. Slider points are labeled strong (≤75th), moderate (75–90th), sparse (90–97.5th), or outside typical support (>97.5th).
- Conditional surface grid: the same 24×24 visible-axis grid, with hidden dimensions fixed by sliders. Values are centered on the outcome training mean. A linear trend plane and zero/mean plane are optional overlays.
- Privacy: aggregate cells are suppressed below N=10. No IDs, raw rows, masks, respondent coordinates, or individual scores are written to Git.
- Default presentation: Extraversion × Emotional Stability, content-balanced ≥2 outcome, empirical/marginal mode, hidden traits at 0 SD.

AA-10's frozen conclusion is preserved: the five-dimensional Ridge model is descriptive/predictive and cross-sectional; it does not establish causality, a theory of change, or a population-optimal wellbeing surface.
