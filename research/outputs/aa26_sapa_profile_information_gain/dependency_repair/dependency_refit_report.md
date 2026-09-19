# Affected human dependency refits

All five flagged dependencies materially changed and were refit under the frozen two-item multi-item-proxy rule. These are corrected analyses, not verification of unchanged scores. Original artifacts remain historical.

| Analysis | Corrected eligible N | Test N | Delta R² | 95% paired interval | Decision |
|---|---:|---:|---:|---|---|
| AA20 | 1179 | 243 | +0.0010 | [-0.0186, +0.0193] | B. Reliable association without incremental validity |
| AA22 | 1484 | 301 | +0.0654 | [+0.0330, +0.0976] | increment interval excludes zero |
| AA23 | 1473 | 294 | +0.1119 | [+0.0723, +0.1528] | increment interval excludes zero |
| AA24 | 1179 | 243 | +0.0006 | [-0.0188, +0.0208] | increment not established |
| AA21_common | 1179 | 236 |  |  | corrected common-sensitivity refit; primary unchanged |

AA-21 common sensitivity held-out R² is 0.4853; its primary coefficients, primary human performance, and persona constructions were not rerun.

AA-20 repeats the original aggregate association, bootstrap, indicator, repeated-split, factor-count/C3, bridge, and dominant-trait checks. AA-22/23 repeat the human fit and human full-sample weight portions. AA-24 repeats human predictions and human axis-weight sensitivity. No saved model matrices were loaded and no persona was rescored. Consequently, old persona transports and correlations dependent on changed human weights remain withdrawn/stale; this report does not claim those downstream products have been repaired. Original AA-12/13 withdrawals are also unchanged.

The repair isolates eligibility: historical full-cohort item standardization remains in AA-22/23/24 and AA-21 common sensitivity, as in their source implementations. New AA-26 candidate evaluation uses training-only predictor preprocessing. Fixed-test bootstrap intervals condition on fitted predictions, not full refitting. The AA-20 factor_analyzer compatibility shim only renames an sklearn argument; it does not alter the estimator.

This report is generated before candidate-effect interpretation. CPU-only; no RunPod/paid compute/GPU/model inference/viewer changes.
