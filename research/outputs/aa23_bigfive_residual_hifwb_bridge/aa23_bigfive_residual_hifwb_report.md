# AA-23 Big Five-residual trait bridge to HiFWB

**Headline decision: exploratory residual signal.** The 41 AA-19 direct trait proxies were residualized against the human Big Five using training respondents only. The residual index was tested against HiFWB and transported after analogous within-model residualization.

## Human held-out comparison

| Model | Test N | R² | RMSE |
|---|---:|---:|---:|
| BigFive | 673 | 0.468 | 0.602 |
| ResidualTraitIndex | 673 | 0.054 | 0.802 |
| BigFive_plus_ResidualTraitIndex | 673 | 0.542 | 0.558 |

The residual-index increment over Big Five is ΔR²=+0.075, paired test-resample 95% interval [+0.037, +0.114].

## Transport

Against AA-21 expanded Big Five scores, residual-versus-Big-Five persona-score Pearson/Spearman correlations are: Gemma 0.015/0.042; Llama 0.009/0.151; Qwen 0.018/0.016. These are relative rankings, not calibrated wellbeing estimates.

## Limits

Residualization removes linear Big Five overlap; it does not establish causal independence or a new psychological construct. The bridge remains sparse and semantically mapped, and SAPA planned missingness is handled by observed-weight renormalization. No model inference or paid compute occurred.
