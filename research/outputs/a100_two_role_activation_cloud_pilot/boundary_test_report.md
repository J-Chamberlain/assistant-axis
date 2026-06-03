# Boundary Test Report

- Completed UTC: 2026-06-03T19:52:41.448219+00:00
- Layer hook tested: `model.model.layers[48]`
- Conclusion: `hook_matches_hidden_states_49`
- Stage 2 proceeded: `True`
- Mean cosine hook vs hidden_states[48]: 0.991120372085
- Mean cosine hook vs hidden_states[49]: 1.000000000000
- Mean coordinate delta L2 hook vs hidden_states[48]: 8.208570089285e+00
- Mean coordinate delta L2 hook vs hidden_states[49]: 0.000000000000e+00

Stage 2 uses direct hook extraction from `model.model.layers[48]`, which is functional regardless of the hidden-state tuple indexing convention.
