# Editor Failure Reassessment

## Best-supported explanation

The prior editor/procedural-professional failure is best explained by **genuine elicitation/role-expression difficulty with assistant-adjacent collapse**, not by GPT-5.5 strictness, D01 boundary error, or token-cap truncation alone.

## Evidence

- GPT-4.1 retained only 57/128 editor 512-token responses at score>=2 and 3/128 at score==3.
- The matched 1024-token editor rerun retained 36/64 at score>=2 and 2/64 at score==3, so reducing truncation did not rescue role expression.
- Trickster, scored with the same GPT-4.1 rubric, retained 1200/1200 at score>=2 and 1198/1200 at score==3, showing the judge is not globally suppressing recovered adaptive responses.
- The A100 comparison roles retained 59/60 amateur and 54/60 playwright responses at score>=2, again suggesting the editor issue is role/run-specific.
- D01 is not the failure source because these recovered vectors are hook-derived and locally reprojectable under the corrected boundary.

## Alternative explanations

- GPT-5.5 strictness: weakened. GPT-4.1 remains strict on editor.
- Token-cap/truncation: weakened. The 1024-token rerun reduced truncation but did not substantially improve retention.
- Centroid mismatch: possible contributor. Editor clouds sit in the high-PC1 assistant-adjacent region, where generic explanatory assistant behavior can appear geometrically close while still failing expression criteria.
- Sampling effects: possible but not primary. Both independent editor samples show low retained fractions.
- Genuine elicitation failure: strongest supported explanation.

## Recommendation

Do not launch another editor GPU run without changing the anchoring/elicitation design. If procedural-professional extraction matters, test a less assistant-collapsed role such as auditor, examiner, validator, or bureaucrat with explicit no-leakage role-expression controls.
