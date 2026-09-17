# AA-24 model-consensus-axis HiFWB transport

**Headline decision: restricted model-consensus hypothesis.** The independently frozen AA-18 C1–C3 consensus axes were evaluated as a separate human-associated wellbeing representation. C4/C5 were excluded because AA-19 found their direct human bridge coverage inadequate.

## Human held-out comparison

| Model | Test N | R² | RMSE |
|---|---:|---:|---:|
| BigFive | 564 | 0.494 | 0.586 |
| Consensus_C1_C3 | 564 | 0.178 | 0.746 |
| BigFive_plus_Consensus_C1_C3 | 564 | 0.498 | 0.583 |

The combined consensus-axis increment beyond Big Five is ΔR²=+0.005, paired test-resample 95% interval [-0.007, +0.017]. The interval crosses zero, so this is not validated incremental human wellbeing structure.

## Persona transport

Full-sample human association weights were applied to the AA-18 C1–C3 scores for all 275 Qwen, Llama, and Gemma personas. The resulting values are relative model-consensus hypotheses, not calibrated wellbeing estimates. Train+validation versus full-sample score ranking sensitivity and correlations with AA-21/AA-23 are in `projection_convergence_comparison.csv`.

## Limits

This result uses a sparse provisional human bridge and the same saved model-derived axes used in AA-19/AA-20. It does not establish causal traits, human/model equivalence, model subjective wellbeing, or predictive validity in new humans. C4/C5 remain untested; the projection is intentionally restricted to C1–C3. No model inference or paid compute occurred.
