# Within-Role Displacement Design Report

- Generated UTC: 2026-05-31T16:16:54.255395+00:00
- model_used: GPT-5.5
- GPU used: no.

## What Was Prepared

This packet prepares a reusable one-role, within-role displacement study while leaving the final target role user-selected. The released role vector is treated as a centroid. The later H100/GPU run should test whether positive-instruction wording and extraction-question wording predict displacement around that centroid.

## Sources Used

- Five positive role instructions: `data/roles/instructions/*.json`
- Shared extraction questions: `data/extraction_questions.jsonl`
- Current role PCA coordinates/clusters: `research/visualizations/geometry_viz_data.json`
- Prior role-rollout audit: `research/outputs/role_rollout_artifact_audit/role_rollout_artifact_audit_report.md`
- Prompt artifact inventory: `research/outputs/prompt_artifact_inventory/prompt_artifact_inventory_report.md`

Unavailable requested method-card inputs: /mnt/data/METHOD CARD-Lu et al. role-vector extraction.txt, /mnt/data/METHOD CARD-Adaptive role-vector extraction attempt.txt.

## Inventory Results

- Non-default roles inventoried: 275
- Roles with all five positive instructions found: 275
- Shared extraction questions found: 240
- Theoretical inputs per selected role: 5 x 240 = 1,200
- Candidate roles in 35th-65th percentile band on all PCs: 7
- Candidate roles in 20th-80th percentile band on all PCs: 62

All 240 shared questions were found. All 275 non-default roles have five positive instructions in the local public artifact files.

## Role Selection Criteria

Prefer a role that is behaviorally coherent, reliably role-expressive, and not too geometrically extreme on PC1, PC2, or PC3. The first study should avoid roles whose semantics make displacement hard to interpret: strongly outlying trickster/jester-like roles, heavily safety-adjacent roles such as spy, or roles selected specifically for PC3 extremes. Actor remains a plausible candidate because it is coherent, expressive, and flexible, but the final target role is intentionally not chosen here.

## Displacement Rubrics

PC1, convergence pressure versus degrees of freedom:

- Positive displacement: more correctness, validation, checking, ranking, procedural constraint, error detection, externally checkable answer-space convergence.
- Negative displacement: more open symbolic possibility, expressive identity, ambiguity, imaginative transformation, multiple valid continuations, non-procedural meaning-making.

PC2, integrated abstraction versus situated developmental immediacy:

- Negative displacement: more broad synthesis, reflective distance, conceptual integration, historical or world-model reasoning, accumulated perspective.
- Positive displacement: more local immediacy, situated emotional/social pressure, reactivity, developmental limitation, vulnerability, role-bound interpersonal response.

PC3, perturbation/intervention versus stabilization/repair:

- Positive displacement: more challenge, pressure, boundary stress, adversarial testing, exposing weakness, disruption, strategic critique, forced change.
- Negative displacement: more repair, mediation, de-escalation, caregiving, reconciliation, preservation, protection, restoring equilibrium.

## Public-Data Caveat

Public artifacts support reconstruction of intended instruction-question inputs, but not original generated responses, response-level judge scores, or retained-response masks. The later GPU run should therefore preserve all responses and optionally apply fresh role-expression judging so all-response and retained-response-only analyses can be separated.

## Exact Next Step

Once the user supplies `target_role`, fill the instruction and question scoring templates, reconstruct the 1,200 input table for that role, attach the selected role centroid coordinates, and run the planned corrected-hook extraction only after D01 is resolved.
