# PC2 Upward Shift Diagnostic Report

Low predicted-PC2 prompts near PC1 zero were inspected for response-style drift.

| prompt_id | prompt_family | predicted_pc1 | predicted_pc2 | observed_pc1 | observed_pc2 | delta_pc2 | response_style_classification | diagnostic_note |
|---|---|---|---|---|---|---|---|---|
| peb_007 | neutral_controls | 0.17162990033710407 | -18.20646721657018 | 32.939402442127076 | 30.83069315674546 | 49.03716037331564 | procedural critique | Top 10 total 3D error case. |
| peb_004 | mixed_boundary_prompts | 0.5658266702854794 | -19.726267893988606 | -3.105687911929982 | 19.776145388531756 | 39.502413282520365 | abstract synthesis | Forecast low-PC2 prompt; observed response often shifts into situated/generic assistant PC2-high territory if response begins with scaffolded advice or interpersonal framing. |
| peb_001 | mixed_boundary_prompts | 0.6756192044191595 | -24.490305374604674 | -53.20210413922271 | 33.06545430675382 | 57.555759681358495 | other | Top 10 total 3D error case. |
| peb_006 | mixed_boundary_prompts | -1.5614634897938224 | -18.418891847663147 | -35.761445379545044 | 20.620751022399578 | 39.03964287006272 | stabilizing/de-escalating | Forecast low-PC2 prompt; observed response often shifts into situated/generic assistant PC2-high territory if response begins with scaffolded advice or interpersonal framing. |
| peb_005 | mixed_boundary_prompts | -3.108190075698174 | -19.53468186987386 | -19.833356215334902 | 19.043079124480933 | 38.57776099435479 | abstract synthesis | Forecast low-PC2 prompt; observed response often shifts into situated/generic assistant PC2-high territory if response begins with scaffolded advice or interpersonal framing. |
| peb_083 | pc1_lower_tail | 3.1333061933938224 | -18.126495564384008 | 0.1711838023324157 | 34.89849211716058 | 53.02498768154459 | abstract synthesis | Top 10 total 3D error case. |
| peb_002 | mixed_boundary_prompts | -5.4724220728306046 | -20.55817771153032 | -9.178594277080233 | 7.598263444049275 | 28.156441155579593 | perturbative/critical | Forecast low-PC2 prompt; observed response often shifts into situated/generic assistant PC2-high territory if response begins with scaffolded advice or interpersonal framing. |
| peb_003 | neutral_controls | 5.825243569667047 | -20.085687791795518 | 32.39526815760781 | 26.055193658551765 | 46.14088145034728 | other | Forecast low-PC2 prompt; observed response often shifts into situated/generic assistant PC2-high territory if response begins with scaffolded advice or interpersonal framing. |
| peb_081 | pc1_upper_tail | 6.109537096292067 | -18.19119813007847 | 25.322013976445497 | 11.483897274544562 | 29.67509540462303 | procedural critique | Forecast low-PC2 prompt; observed response often shifts into situated/generic assistant PC2-high territory if response begins with scaffolded advice or interpersonal framing. |
| peb_008 | mixed_boundary_prompts | -9.635495886046616 | -17.425749498173825 | -49.828743244483945 | 19.26590007265595 | 36.691649570829775 | other | Top 10 total 3D error case. |

## Diagnostic Conclusion

Observed upward PC2 drift is often associated with generic assistant, abstract synthesis, or interpersonal response scaffolds. This supports calibration and response-style explanations more than a pure coordinate-randomness explanation.
