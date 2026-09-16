# SAPA Human Wellbeing Terrain Explorer — implementation report

## Observed inputs

SAPA V5 (23,679 respondents; 696-item matrix) was read locally from the verified AA-10 source. Big Five coordinates use the frozen AA-10 keyed item definitions and observed-only scoring. The all-five-domain terrain cohort is N=8,585. Wellbeing uses the frozen 13 direct items and content groupings; Community is unavailable in the source mapping.

## Views

The explorer provides selectable Big Five X/Y axes, ten frozen wellbeing outcomes, observed/marginal aggregate surfaces, conditional five-dimensional Ridge slices, hidden-trait sliders in SD units, 2D heatmaps, 3D surfaces, a trend-plane toggle, and a zero/sample-mean plane. Aggregate cells with N<10 are suppressed. Conditional surfaces are model estimates and do not imply causal slider effects.

## Limits

Model selection is human-only and deterministic. The terrain is a sample visualization, not a population probability distribution or clinical threshold. No respondent-level rows, IDs, masks, or completed profiles are included in the committed bundle.
