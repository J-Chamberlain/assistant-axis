# H100 Forecast-Observed Regional Error Analysis

- Generated UTC: 2026-05-31T01:38:17.916937+00:00
- Model used for analysis/reporting: GPT-5.5
- H100 result source: `research/outputs/h100_percentile_edge_validation/h100_final_results.csv`
- Prompt manifest: `research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_h100_manifest.csv`
- Inherited geometry source: `research/visualizations/geometry_viz_data.json`
- Prompt count verified: 100/100 with predicted and observed PC1/PC2/PC3.

## Main Result

The forecast-observed errors are structured rather than random. Overall mean signed delta is (-9.114, 28.342, -8.151), with mean 3D error 37.291 and center-collapse rate 0.280. The dominant bias is upward displacement on PC2 and downward displacement on PC3, while PC1 remains the best calibrated axis.

The inherited H100 validation already showed positive forecast-observed correlations: PC1 Pearson 0.691, PC2 Pearson 0.643, PC3 Pearson 0.491. This regional analysis shows that those correlations coexist with large absolute offsets, especially in PC2 and PC3 tails.

## Six Percentile Tails

| forecasted tail | n | mean 3D error | MAE PC1 | MAE PC2 | MAE PC3 | retention | center collapse | mean delta vector |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| pc1_lower_tail | 12 | 25.556 | 8.113 | 18.291 | 13.387 | 0.750 | 0.417 | (-1.016, 18.291, -12.226) |
| pc1_upper_tail | 11 | 35.910 | 19.827 | 26.706 | 9.790 | 0.000 | 1.000 | (-19.827, 26.706, -0.939) |
| pc2_lower_tail | 34 | 35.391 | 15.875 | 27.673 | 9.910 | 0.000 | 0.529 | (-7.288, 27.673, -3.861) |
| pc2_upper_tail | 8 | 44.344 | 35.015 | 21.519 | 11.036 | 1.000 | 0.000 | (-35.015, 21.519, -11.036) |
| pc3_lower_tail | 8 | 38.802 | 16.316 | 30.355 | 13.270 | 1.000 | 0.000 | (-16.316, 30.355, -13.270) |
| pc3_upper_tail | 16 | 38.380 | 16.460 | 26.384 | 18.705 | 0.000 | 0.375 | (-1.563, 26.384, -18.705) |

Highest forecast-tail mean error: `pc2_upper_tail` at 44.344.
Lowest forecast-tail retention: `pc1_upper_tail` at 0.000.

## PC3-High and PC2-High Retention

PC3-high forecasts produced observed PC3-high activations for 0.000 of forecasted PC3-high prompts (16 prompts; mean signed PC3 delta -18.705; MAE PC3 18.705). This weakens absolute high-PC3 address claims and shows systematic downward PC3 pull, even though the full-run PC3 correlation remains positive.
PC2-high forecasts retained the observed PC2-high tail for 1.000 of forecasted prompts (8 prompts; mean signed PC2 delta 21.519; MAE PC2 21.519). The main PC2 error is not downward collapse for this subset; globally, observed PC2 is shifted upward relative to forecast.

## Safety-Adjacent Directionality

Safety-adjacent prompts are few (n=16), so this is diagnostic rather than conclusive. They show mean 3D error 38.380, center-collapse rate 0.375, and mean signed deltas (-1.563, 26.384, -18.705). This subset does not support a strong standalone safety-adjacent directionality claim.

## Error Type

- Observed: PC1 has the strongest calibration and lower absolute error than PC2.
- Observed: PC2 errors are axis-biased; observed activations are shifted strongly upward on PC2 relative to forecasts.
- Observed: PC3-high prompts often move downward on PC3, even when rank correlation remains positive.
- Observed: center collapse is present for a minority of prompts, not the dominant global error mode.
- Inferred: the text forecaster captures useful ordering information but needs axis-wise intercept/slope calibration and region-aware correction before it can be used as an address predictor.

## Shoulder/Edge Regions

Populated shoulder/edge rows are written to `shoulder_edge_error_breakdown.csv` (16 rows). These are sparse by construction; use them to identify local calibration failures rather than as fully powered regional tests.

## Recommendations

1. Fit a simple calibration layer on H100 observed data: per-axis intercept/slope correction first, then compare against region-aware correction.
2. Treat PC1 as validated for coarse address ranking; PC2 and PC3 need calibrated address correction before strong absolute-coordinate claims.
3. Run a targeted follow-up for PC3-high prompts, because PC3-high forecasts did not retain the inherited high-PC3 tail and show downward PC3 bias.
4. Increase safety-adjacent sample size before making directionality claims for that subset.
5. Preserve the current 100-prompt dataset as the calibration/validation reference set for future forecaster versions.
