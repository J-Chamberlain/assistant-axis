# Persona-by-trait matrix phase gate

**PASS.** All three saved matrices have 275 matched, identically ordered persona rows and 240 identically ordered traits; every cell is finite and signed. Rows are observations and columns are cosine trait-expression variables. No hidden coordinate is a respondent.

| Model | Source SHA256 | Missing | Minimum SD | Maximum absolute skew | Traits with 3×IQR outliers | Effective rank | Ordinary condition | Shrinkage α | Shrinkage condition | Exact / near-duplicate pairs |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen | `723d42415fe3` | 0 | 0.01822 | 1.71 | 12 | 2.95 | 4.52e+10 | 0.012 | 1.01e+04 | 0 / 5 |
| Llama | `74b2cb886967` | 0 | 0.02179 | 4.27 | 111 | 3.38 | 2.59e+09 | 0.024 | 4.3e+03 | 0 / 3 |
| Gemma | `798c0618b9e4` | 0 | 0.003316 | 3.40 | 52 | 3.22 | 5.38e+09 | 0.015 | 7.73e+03 | 0 / 2 |

The saved CSVs were deterministically derived from model-specific released role and trait vectors: average the stored layer vectors for each role and trait, L2-normalize each mean separately, then take the role-by-trait dot product. Thus the values are cosine similarities, not projections, correlations, human ratings, or raw dot products. No across-role centering precedes the cosine; no trait contrast subtraction is documented in this matrix construction. Column centering and scaling happen only inside this analysis. A persona's 240 scores are comparable within its model, and a trait's scores are comparable across that model's personas. Absolute values are not calibrated across models. The construction uses model-specific layer-mean vectors (see the source scripts and provenance audit); the exact original upstream trait-vector extraction recipe remains partly unknown.

Near duplicate components are based on absolute correlation of standardized persona profiles. The inventory records every trait and representative. Ordinary covariance conditioning makes shrinkage necessary.

Sources: `research/outputs/trait_persona_prediction/run_trait_persona_prediction.py`, `research/outputs/multimodel_trait_profile_pc_predictor/run_multimodel_trait_profile_pc_predictor.py`, and `research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md`.
