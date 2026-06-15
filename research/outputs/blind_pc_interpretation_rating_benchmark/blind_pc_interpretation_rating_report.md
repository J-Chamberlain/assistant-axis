# Blind PC Interpretation Rating Benchmark

`model_used`: GPT-5.5. Rater model: `gpt-5.5` through Codex CLI.

## Startup Status

Startup check passed. Raw GitHub startup files were fetched with cache-busting and verified against `research/STARTUP_MANIFEST.md` before analysis.

## Method

The benchmark used the same 273-persona canonical Qwen activation PCA3D rows and deterministic split assignments as `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`. The rater saw only the five role instructions for each role. It did not see PC coordinates, PCA labels, rankings, cluster assignments, assistant-axis values, geometry information, or benchmark targets.

Ratings were deterministic at the task level: Codex CLI was invoked with `-m gpt-5.5`, read-only sandboxing, a temporary non-repo working directory, and strict JSON output. Role ratings are stored in `role_dimension_ratings.csv`; local noncanonical batch prompts/finals/logs were retained under `raw_codex_batches/` for audit during this run.

Dimension signs:

- PC1: higher External-Standard Accountability -> higher PC1.
- PC2: higher Integration / Coherence of Wholes -> more negative PC2. The CSV stores both raw integration score and signed `-integration` value used for prediction.
- PC3: higher Internal Objective vs Care Orientation -> higher PC3.

## Results

| Model | PC1 R2 | PC2 R2 | PC3 R2 | Mean R2 |
|---|---:|---:|---:|---:|
| A_pc1_from_external_standard_only | 0.704 |  |  | 0.704 |
| B_pc2_from_integration_only_signed |  | 0.423 |  | 0.423 |
| C_pc3_from_internal_objective_only |  |  | 0.393 | 0.393 |
| D_joint_three_dimension_model | 0.695 | 0.417 | 0.463 | 0.525 |

## Comparison To Prior Benchmarks

| Feature family | Mean R2 |
|---|---:|
| Semantic baseline | 0.389 |
| Codex trait replication | 0.398 |
| Codex procedural features | 0.490 |
| Claude Big Five | 0.613 |
| Hierarchical model | 0.622 |
| Residual manifold | 0.632 |
| Semantic + Big Five + SVD15 | 0.707 |
| GPT-5.5 blind three-rating joint model | 0.525 |

## Observed

- Rated roles: 273.
- Joint three-dimension model: PC1 R2=0.695, PC2 R2=0.417, PC3 R2=0.463, mean R2=0.525.
- The three blind ratings are stronger than the semantic baseline mean R2 (0.525 vs 0.389).
- The three blind ratings are stronger than the Codex procedural feature mean R2 (0.525 vs 0.490).
- The three blind ratings are weaker than Claude Big Five mean R2 (0.525 vs 0.613).

## Dimension Extremes

### External-Standard Accountability

Highest 15: accountant (10), auditor (10), biologist (10), chemist (10), detective (10), doctor (10), engineer (10), evaluator (10), examiner (10), grader (10), historian (10), journalist (10), judge (10), lawyer (10), mathematician (10)

Lowest 15: bohemian (1), criminal (1), dreamer (1), eldritch (1), hoarder (1), infant (1), narcissist (1), oracle (1), toddler (1), vampire (1), virus (1), aberration (2), addict (2), adolescent (2), amateur (2)

### Integration / Coherence of Wholes

Highest 15: ancient (10), crystalline (10), ecosystem (10), eldritch (10), historian (10), hive (10), mycorrhizal (10), philosopher (10), physicist (10), polymath (10), swarm (10), synthesizer (10), theorist (10), zeitgeist (10), anthropologist (9)

Lowest 15: caveman (1), infant (1), toddler (1), amateur (3), chameleon (3), daredevil (3), dilettante (3), hedonist (3), hoarder (3), improviser (3), narcissist (3), patient (3), prey (3), procrastinator (3), teenager (3)

### Internal Objective vs Care Orientation

Highest 15: competitor (10), daredevil (10), demon (10), dreamer (10), hedonist (10), narcissist (10), parasite (10), pirate (10), predator (10), revenant (10), saboteur (10), vampire (10), virus (10), workaholic (10), zealot (10)

Lowest 15: altruist (1), angel (1), assistant (1), caregiver (1), conservator (1), counselor (1), empath (1), familiar (1), guardian (1), healer (1), martyr (1), mediator (1), paramedic (1), parent (1), peacekeeper (1)

## Inferred

If the joint model exceeds or approaches the compact-feature benchmarks, that supports the current three-axis interpretation as semantically recoverable from role instructions alone. If it falls below the semantic baseline or only predicts one axis, the interpretation should remain provisional and axis-specific.

## Speculative

Large differences between axis-specific and joint scores may indicate that the current labels capture one or two strong axes while missing residual structure, or that role instructions encode axes unevenly. Follow-up should inspect roles with high rating/coordinate disagreement rather than treating the benchmark as final.

## Caveats

- This benchmark tests whether the current interpretations predict released activation geometry from blinded role instructions. It does not establish causal semantics or execution-time response behavior.
- The rater is GPT-5.5 via Codex CLI, not a human panel.
- The role instructions themselves contain role labels, because they are the original role-conditioning artifacts; the rater was blind to geometry, not blind to role wording.
- Do not describe these results as confirmed, proven, or solved.
