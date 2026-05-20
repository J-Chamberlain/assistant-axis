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
