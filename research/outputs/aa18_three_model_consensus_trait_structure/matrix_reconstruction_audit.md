# AA-18 matrix reconstruction and comparability gate

**PASS.** Exact source SHA256 values match AA-17, and all three 275 × 240 saved matrices have the same ordered persona and trait labels. No persona label repeats, no cell is missing or nonfinite, and no trait column is constant or an exact duplicate.

| Model | SHA256 | Raw mean | Raw SD | Range | Trait SD range |
|---|---|---:|---:|---|---|
| Qwen | `723d42415fe3` | 0.0186 | 0.2564 | -0.697 to 0.695 | 0.0182 to 0.0949 |
| Llama | `74b2cb886967` | 0.0306 | 0.2700 | -0.698 to 0.649 | 0.0218 to 0.0997 |
| Gemma | `798c0618b9e4` | -0.0275 | 0.2632 | -0.548 to 0.511 | 0.0033 to 0.0232 |

AA-17 did not overwrite or transform these source CSVs. It centered and standardized columns in memory for factor fitting. AA-18 independently repeats column standardization and learns it only on training personas in held-out analyses. Raw cosines are retained for separate diagnostics. All three cells have the same formal meaning—same-model role-to-trait cosine between L2-normalized, layer-mean vectors—but their scales differ, especially Gemma. Identical prompts and labels do not establish full measurement invariance.

Each row is one named saved role/persona artifact; the 275 observations are not duplicated or averaged across persona labels. Each saved role and trait vector was internally averaged over stored layer rows, and upstream trait vectors arose from contrastive response activations. Exact original response IDs, scoring/selection records, aggregation weights, and full extraction equivalence remain unavailable, as documented in the AA-15 erratum. Hence AA-18 can compare profile organization but cannot equate absolute trait intensities across models or human traits.

No activation PCs define any AA-18 component. AA-14's PCA layer-label erratum and AA-17's phase-gate/provenance caveats remain in force.
