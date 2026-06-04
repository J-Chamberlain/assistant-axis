# Prior Adaptive Run Inventory

Startup status: **STARTUP VERIFIED**.

This audit searched prior adaptive and adjacent extraction artifacts for the
trickster family (`trickster`, `jester`, `joker`, `chaos`) and
procedural/professional family (`editor`, `evaluator`, `assistant`,
`professional`, `administrator`, `worker`, `bureaucrat`, and related terms).

## Candidate Artifact Counts

| artifact_type | count |
| --- | --- |
| csv | 8 |
| json | 28 |
| jsonl | 9 |
| log | 3 |
| md | 32 |
| png | 1 |
| pt | 1398 |
| py | 2 |


## Explicit Prior Adaptive Runs Found

| run_id | role | family | records | score_records | score_ge2 | score_eq3 | truncated | think_artifacts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trickster_phase1_1200 | trickster | trickster_family | 1200 | 64 | 64 | 33 | 733 | 0 |
| editor_phase1_128 | editor | procedural_professional_family | 128 | 128 | 10 | 3 | 99 | 0 |
| editor_matched64_1024 | editor | procedural_professional_family | 64 | 64 | 5 | 1 | 5 | 0 |


Notes:

- No local adaptive extraction run was found for `jester`, `joker`, or a literal `procedural` persona.
- The procedural-professional recovery evidence is represented by the `editor` adaptive runs plus separate professional-hierarchy validation artifacts.
- Full file-level inventory is in `prior_adaptive_artifact_inventory.csv`.
