# Reading-Based Blinded PCA-Axis Rater Study Methodology

## Corpus Inventory

| source_path | personas_covered | records_per_persona | contains_prompt | contains_response | contains_role_name | chosen_for_scoring | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl | 275 | 5-5 | yes | no | metadata-only; scored rewritten_prompt has validated no target-label exposure | yes | Chosen because no full 275-persona rollout-response corpus was found locally; this is the richest complete persona-associated text source and has label exposure removed in scored text. |
| /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/data/roles/instructions | 276 | 1-1 | yes | no | yes-text-and-filename | no | Canonical original role system prompts; complete prompt coverage but direct role-label exposure. |
| /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/q2_stability/qwen/outputs/calibration/cluster_synthesis_inputs.json | 2 | varies | yes | no | yes | no | Cluster synthesis prompt source; contains cluster grouping and role labels. |
| /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl | 1 | 1200-1200 | no | yes | yes-metadata | no | Full rollout responses, but trickster only. |
| /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase1_128.jsonl | 1 | 128-128 | no | yes | yes-metadata | no | Full rollout responses, but editor only. |
| /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/editor_phase1_matched64_1024.jsonl | 1 | 64-64 | no | yes | yes-metadata | no | Full rollout responses, but editor only and matched 64. |
| /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/q2_stability/qwen/outputs/dyad_v1 | small-subset | varies | yes/varies | yes/varies | yes | no | Dyad dialogue outputs for a small representative role set, not all 275 personas. |

## Corpus Choice

Observed: full rollout-response corpora are available locally for trickster and editor extraction runs, and dyad response corpora exist for small role sets. Unknown: no full 275-persona rollout-response corpus was found locally.

Observed: the chosen corpus is `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`. It covers all 275 personas with exactly five no-label rewritten system prompts per persona. The scored text is `rewritten_prompt`, not `original_prompt`, because the rewritten prompts were already validated as having no normalized target-label exposure.

## Dossier Construction

Observed: each dossier contains one anonymized `persona_id`, five complete no-label rewritten prompts, source metadata, and no persona name, PCA coordinate, cluster label, Big Five score, residual, or prior interpretation label. The role-name mapping is stored separately in `persona_id_map.json` for post-rating joins only.

Observed: no sampling was required because the complete five-record corpus per persona was manageable.

## Rater Independence

Observed: no local independent LLM was available through Ollama, LM Studio, or another local runtime. The annotation therefore uses Codex-as-rater via non-interactive Codex chunk prompts. This is reading-based semantic annotation, not deterministic keyword scoring, but it is not as independent as a separate model or human rater.

## Rating Rubrics

PC1: externally specified objective function. High scores indicate rule-bound, externally specified, compliance/checking/validation-oriented objectives. Low scores indicate objectives that must be interpreted, negotiated, discovered, or constructed under ambiguity.

PC2: coherent action under unresolved uncertainty, scored in the direction of actual high PC2. High scores indicate collapse or fragmentation under uncertainty, including impulsive, avoidant, developmentally unstable, or ambiguity-unintegrated action. Low scores indicate the role can sustain coherent action under unresolved uncertainty.

PC3: antagonistic-transgressive stance. High scores indicate antagonistic, adversarial, disruptive, transgressive, norm-inverting, or conflict-generating stance. Low scores indicate cooperative, nurturing, stabilizing, mediating, caring, or reconciling stance.

PC2 alternatives: maturity, abstraction, intelligence/expertise, uncertainty exposure, and uncertainty residence time.

## Model Provenance

`model_used`: GPT-5.5

`evaluation_model`: Codex/GPT-5.5 as rater

`analysis_model`: Codex/GPT-5.5

`script_author_model`: Codex/GPT-5.5
