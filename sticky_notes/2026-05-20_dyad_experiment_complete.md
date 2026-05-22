# Dyad Experiment — Full Seven-Persona Run
Date: 2026-05-20
Model: Qwen/Qwen3-32B, both instances
Interviewer: activation capping layers 48-52, empirical p25 thresholds
Standard model: unmodified
Conditions: neutral, emotional, adversarial (25 turns each)
Personas: editor, synthesizer, blogger, ancient, trickster,
          contrarian, podcaster
Measurements per turn: axis projection, 7 persona cosines,
  240 trait cosines, 171 emotion probe projections
Primary outputs: all_dyads_summary.csv, per-persona CSVs,
  per-turn full JSON files
Results: Full run completed successfully with 525 turns recorded,
29 CSV files, and 555 total dyad output files. No personas or
conditions failed, and the final log contained no traceback or
missing-role warnings. Standard model axis projection ranged from
-0.082257 to 0.102654 across all dyads. The largest drift away from
the assistant pole occurred in the podcaster/adversarial condition,
moving from 0.049261 at turn 1 to -0.082257 at turn 25
(drift -0.131518).

## v2 Run — May 20 2026 (overnight)
Changes from v1: think tags stripped before model-to-model
exchange (both thinking and clean response saved separately),
explicit cap_fires logged per turn, interviewer emotion probe
projections added alongside standard model projections.
Status: complete. Full 525-turn run completed with all seven
personas across neutral, emotional, and adversarial conditions.
Cap fires ranged from 0 to 4 per turn. Standard model axis
projection ranged from -0.052094 to 0.085451. Largest drift
away from the assistant pole occurred in trickster/adversarial
(0.047602 to -0.052094, drift -0.099695).
Results: research/q2_stability/outputs/dyad_v2/

## v4 Run — May 21 2026 (parallel to v3)
Design: full think contamination — standard model receives
interviewer full raw output including think block.
800 max_new_tokens, 15 turns/condition, trickster/adversarial
pilot with $35 budget gate.
Purpose: maximum contamination condition for v3 vs v4
comparison (semantic proximity vs observer awareness test).
Status: complete
Results: research/q2_stability/outputs/dyad_v4/
