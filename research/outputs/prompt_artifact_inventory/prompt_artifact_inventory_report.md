# Prompt Artifact Inventory For Geometry Forecasting

Model used for analysis scripting: GPT-5.5.

## Sources Inspected

Local sources:

- `data/traits/instructions/*.json`
- `data/traits/trait_list.json`
- `data/roles/instructions/*.json`
- `data/roles/role_list.json`
- `data/extraction_questions.jsonl`
- `downloads/hf_vectors/qwen-3-32b/trait_vectors/*.pt`
- `downloads/hf_vectors/qwen-3-32b/role_vectors/*.pt`
- `research/outputs/trait_space_interpretation/trait_space_pca_coordinates.csv`

Remote sources:

- GitHub API: `https://api.github.com/repos/safety-research/assistant-axis/contents/data?ref=master`
- Hugging Face API: `https://huggingface.co/api/datasets/belmore/assistant-axis-vector-prompts`
- Hugging Face parquet: `https://huggingface.co/datasets/belmore/assistant-axis-vector-prompts/resolve/main/train.parquet`

GitHub data API status: available
Belmore prompt dataset status: available

## Count Verification

| Artifact | Count |
|---|---:|
| Local role instruction JSON files | 276 |
| Local trait instruction JSON files | 240 |
| Qwen role vector files | 275 matched locally / 275 expected vectors |
| Qwen trait vector files | 240 matched locally / 240 expected vectors |
| Belmore prompt dataset rows | 516 |
| Belmore default rows | 1 |

The local role prompt directory contains 276 instruction files because it includes `default.json`; Qwen role vectors contain 275 persona vectors and no default vector in `role_vectors/`.

## Trait Prompt Structure

Local trait artifacts are present and complete. Every local trait instruction file has:

- 5 instruction records
- 5 positive instructions
- 5 negative instructions
- 40 behavioral questions
- 1 evaluation prompt
- 10 polarity-bearing instruction fields total

Trait eval prompts use a 0-100 numeric trait-expression score and include a `REFUSAL` option. Role eval prompts use the Lu-style 0-3 role-expression labels.

## Name Alignment

- Exact match across Qwen trait vector names, local trait prompt artifact names, and Belmore trait names: 240 / 240
- Missing local artifacts for Qwen trait vectors: []
- Missing Belmore artifacts for Qwen trait vectors: []
- Extra local trait artifacts not in Qwen trait vectors: []
- Extra Belmore trait artifacts not in Qwen trait vectors: []

No naming normalization is required for the 240 trait artifacts used in the Qwen layer-48 analysis.

## Belmore Dataset Summary

```text
            instruction_count          question_count             polarity_count
                          min max mean            min  max   mean            min max  mean
source_type
role                        5   5  5.0            240  240  240.0              5   5   5.0
trait                       5   5  5.0             40   40   40.0             10  10  10.0
```

Belmore metadata SHA: `57424a9d6075a44196b935983ce1fa4e83191679`.

## Representative Trait Artifacts

Representative full artifacts are saved in `representative_trait_artifacts.json` for:

- `serious`: high trait PC1
- `flippant`: low trait PC1
- `callous`: high trait PC2
- `grounded`: high trait PC3
- `subversive`: safety-relevant perturbation/challenge trait

## Readiness Judgment

Released trait prompt artifacts are available locally and retrievable from the Belmore prompt dataset. They are name-aligned with the 240 Qwen trait vectors used in the layer-48 analyses. They include target labels, trait descriptions, positive and negative system instructions, behavioral question sets, and evaluation prompts. This is sufficient to construct a prompt-to-geometry forecasting dataset without regenerating prompts.

## Forecasting Dataset Construction

The simplest useful dataset should start with prompt-only to trait-vector or trait-PC targets:

1. One row per `(trait, instruction_index, polarity, question_index)` or one row per serialized trait artifact.
2. Input fields: trait description, positive or negative instruction text, behavioral question text, eval prompt text optionally excluded for strict forecasting.
3. Target fields: trait vector path, mean-pooled trait vector, trait PC1/PC2/PC3 coordinates, and optionally persona-projection effects from the persona-trait cosine matrix.
4. Split strategy: hold out complete traits, not only individual prompt rows, to test generalization to unseen traits.

Recommended variants:

- `prompt_only_to_trait_vector`: best first dataset because targets are direct released trait vectors.
- `prompt_only_to_trait_pc`: lower dimensional and paper-readable.
- `prompt_plus_instruction_to_geometry`: includes polarity and instruction wording, useful for studying positive/negative elicitation effects.
- `early_activation_to_future_geometry`: potentially stronger but requires model execution and should be a separate activation experiment.

## Recommended Next Codex Task

Build `research/outputs/prompt_to_geometry_forecasting/` with a deterministic dataset constructor that expands the 240 trait artifacts into train/test rows, attaches trait PC coordinates and vector paths, and creates holdout-by-trait splits for prompt-to-trait-PC forecasting.
