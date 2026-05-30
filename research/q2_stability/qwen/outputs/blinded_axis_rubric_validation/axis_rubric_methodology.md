# Blinded Axis Rubric Validation Methodology

## Corpus Audit

Observed: the validation used `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl` as the full persona-associated text corpus. It contains 1,375 prompt records covering 275 personas with exactly five prompts per persona. The scored text field was `rewritten_prompt`, produced by the no-label prompt-ablation workflow. `original_prompt` and `role_description` are present but were not used for scoring because the study is intended to avoid role-name and label exposure.

Observed: the corpus is not a full rollout-response corpus. It is a full five-prompt-per-persona system-prompt corpus. No broader 275-persona full response corpus was identified in the canonical tracker files during this pass.

Observed: no sampling was used. The five no-label prompts for each persona were concatenated in prompt order.

## Blinding

Observed: scoring occurred before PCA coordinates, clusters, residuals, or prior interpretation labels were joined. The scoring function used only no-label prompt text and retained `persona` only as a row identifier for later joining.

## Scoring Method

Observed: no external model or API calls were made. Because a local independent LLM judge was not available in this session, the study used deterministic coordinate-blind lexical-semantic rubric proxies. This is weaker than an independent human or model semantic-rating study and should be treated as an initial validation screen, not a final blinded adjudication.

Inferred: the proxy is still useful because it tests whether the working axis interpretations have recoverable signal in full prompt text without using persona names or PCA coordinates.

## Rubrics

PC1 score: high values indicate externally specified objectives, constraints, standards, rules, and ambiguity reduction. Low values indicate internally negotiated objectives, open possibility, interpretation, and ambiguity maintenance.

PC2 score: despite the requested column name `pc2_coherent_action_under_uncertainty_score`, high values operationalize the high-PC2 side of the current interpretation, namely fragmented or poorly integrated action under uncertainty. Low values indicate sustained coherent action under uncertainty. This direction was chosen so positive score-PC correlation is the target-aligned result.

PC3 score: high values indicate antagonistic, disruptive, adversarial, or transgressive stance. Low values indicate cooperative, stabilizing, caring, reconciling, or system-maintaining stance.

## Alternative PC2 Rubrics

The rival PC2 pass computed lexical proxies for maturity risk, abstraction, openness, intelligence or expertise, uncertainty exposure, uncertainty residence time, and an integrated-uncertainty alternative. These were used to test whether the current PC2 formulation outperforms simpler explanations.

## PCA Coordinates

Actual coordinates were loaded from `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/visualizations/geometry_viz_data.json` after scoring. The validation uses the embedded persona PCA coordinates in the visualization dataset, covering 275 personas.

## Model Provenance

`model_used`: GPT-5.5. The model wrote and orchestrated the script; the numeric scores were produced by deterministic local code, not model inference.
