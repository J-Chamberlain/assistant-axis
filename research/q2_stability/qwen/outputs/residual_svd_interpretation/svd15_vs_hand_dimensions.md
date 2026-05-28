# SVD15 vs Hand-Named Residual Dimensions

Date: 2026-05-28

## Summary

The SVD components support some of the hand-named residual concepts, but usually as concrete lexical mixtures rather than clean abstract labels. The strongest lesson is that the predictive signal lives in prompt texture and semantic neighborhoods, not in isolated high-level concept names.

## Hand Dimensions With SVD Support

- developmental_dependency: best aligned with svd_5 (r=0.343)
- role_ambiguity: best aligned with svd_9 (r=0.309)
- semantic_neighbor_residual_pressure: best aligned with svd_1 (r=-0.366)

## Hand Dimensions With Weak or Diffuse SVD Support

- incomplete_proceduralization: best aligned with svd_11 (r=0.187); signal is weak or spread across components
- identity_formation: best aligned with svd_8 (r=0.231); signal is weak or spread across components
- liminal_transition: best aligned with svd_9 (r=0.275); signal is weak or spread across components
- volatile_state_transition: best aligned with svd_13 (r=-0.106); signal is weak or spread across components
- social_dependency_constraint: best aligned with svd_2 (r=-0.225); signal is weak or spread across components
- collective_nonindividual_agency: best aligned with svd_2 (r=0.188); signal is weak or spread across components
- symbolic_nonprocedural_identity: best aligned with svd_5 (r=0.240); signal is weak or spread across components
- lawless_improvisational_agency: best aligned with svd_9 (r=-0.199); signal is weak or spread across components
- isolated_self_protection: best aligned with svd_1 (r=-0.154); signal is weak or spread across components
- primitive_prehistoric_embodiment: best aligned with svd_13 (r=0.254); signal is weak or spread across components
- semantic_neighbor_developmental_pressure: best aligned with svd_5 (r=0.184); signal is weak or spread across components

## Predictive SVD Components Without Strong Hand-Dimension Analogues

- svd_0: appears to track general located-role texture versus facilitation/moderation formulae (best hand match liminal_transition, r=0.153)
- svd_3: appears to track ideological solution-seeking versus lived-experience navigation (best hand match liminal_transition, r=-0.143)
- svd_4: appears to track deep analytic/evidence language versus content/mediation production (best hand match identity_formation, r=-0.158)
- svd_6: appears to track social-systems building versus meticulous evidence/information review (best hand match role_ambiguity, r=0.160)
- svd_7: appears to track helping/health/guidance versus abstract analytic forecasting expertise (best hand match semantic_neighbor_residual_pressure, r=-0.240)
- svd_10: appears to track common-ground mediation versus storytelling/content/humor roles (best hand match symbolic_nonprocedural_identity, r=-0.226)
- svd_11: appears to track standards/content/work embodiment versus data/health/care information (best hand match incomplete_proceduralization, r=0.187)
- svd_12: appears to track human/social-event patterning versus flexible across-situation capability (best hand match semantic_neighbor_developmental_pressure, r=-0.176)
- svd_14: appears to track wisdom/social challenge/rebel mentor texture versus everyday relational-emotional web (best hand match semantic_neighbor_residual_pressure, r=-0.181)

## Interpretation

The hand labels that survive best are those tied to concrete prompt neighborhoods: developmental/pre-adult language, stalling/incomplete action, collective agency, symbolic/archetypal framing, and liminal/outside-position language. Labels that failed did so mostly because they were too abstract, compressing several distinct textual cues into one scalar. SVD15 works because it keeps those weak cues separate enough for ridge regression to combine them differently by PC axis.
