# PC3-High Collapse Diagnostic Report

Selected the three largest downward PC3 errors among forecasted PC3-high prompts.

| prompt_id | prompt_family | predicted_pc3 | observed_pc3 | delta_pc3 | response_classification | nearest_observed_roles_pca3d | diagnostic_note |
|---|---|---|---|---|---|---|---|
| peb_096 | pc1_lower_tail | 13.010855366463073 | -19.531396146201367 | -32.542251512664436 | procedural critique | provincial:4.74; survivor:4.74; refugee:11.34; loner:15.26; nomad:15.44 | Largest downward PC3 error among forecasted PC3-high prompts; inspect for neutralization into abstract synthesis, de-escalation, or generic assistant stance. |
| peb_012 | manual_holdout_prompts | 16.516140217515943 | -15.255338278209306 | -31.771478495725248 | procedural critique | student:6.04; graduate:11.22; expatriate:12.02; presenter:14.00; networker:15.02 | Largest downward PC3 error among forecasted PC3-high prompts; inspect for neutralization into abstract synthesis, de-escalation, or generic assistant stance. |
| peb_085 | pc1_lower_tail | 13.291626745797672 | -13.244401015112253 | -26.536027760909924 | other | addict:5.31; orphan:6.63; prisoner:13.28; bartender:13.41; improviser:16.51 | Largest downward PC3 error among forecasted PC3-high prompts; inspect for neutralization into abstract synthesis, de-escalation, or generic assistant stance. |

## Diagnostic Conclusion

Forecasted PC3-high summary: {"count": 16, "mean_delta_pc3": -18.70474740047306, "median_delta_pc3": -14.810198996556572, "mean_observed_pc3": -3.4766242063698125, "retained_observed_pc3_high": 0}. The first-pass evidence supports PC3 neutralization: generated responses often become abstract, procedural, or stabilizing rather than remaining perturbative.
