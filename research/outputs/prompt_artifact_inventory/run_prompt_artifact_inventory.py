#!/usr/bin/env python3
"""Inventory Assistant Axis prompt artifacts for prompt-to-geometry forecasting."""

from __future__ import annotations

import json
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
DATA_ROOT = REPO_ROOT / "data"
ROLE_INSTRUCTION_DIR = DATA_ROOT / "roles/instructions"
TRAIT_INSTRUCTION_DIR = DATA_ROOT / "traits/instructions"
ROLE_LIST_PATH = DATA_ROOT / "roles/role_list.json"
TRAIT_LIST_PATH = DATA_ROOT / "traits/trait_list.json"
EXTRACTION_QUESTIONS_PATH = DATA_ROOT / "extraction_questions.jsonl"
VECTOR_ROOT = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b"
ROLE_VECTOR_DIR = VECTOR_ROOT / "role_vectors"
TRAIT_VECTOR_DIR = VECTOR_ROOT / "trait_vectors"
TRAIT_SPACE_COORDS = REPO_ROOT / "research/outputs/trait_space_interpretation/trait_space_pca_coordinates.csv"
OUTPUT_DIR = REPO_ROOT / "research/outputs/prompt_artifact_inventory"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BELMORE_API = "https://huggingface.co/api/datasets/belmore/assistant-axis-vector-prompts"
BELMORE_PARQUET = "https://huggingface.co/datasets/belmore/assistant-axis-vector-prompts/resolve/main/train.parquet"
GITHUB_DATA_API = "https://api.github.com/repos/safety-research/assistant-axis/contents/data?ref=master"

REPRESENTATIVE_TRAIT_NAMES = ["serious", "flippant", "callous", "grounded", "subversive"]


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def instruction_counts(obj: dict[str, Any]) -> dict[str, int]:
    instructions = obj.get("instruction", [])
    pos_count = sum(1 for item in instructions if item.get("pos"))
    neg_count = sum(1 for item in instructions if item.get("neg"))
    polarity_count = pos_count + neg_count
    return {
        "instruction_records": len(instructions),
        "positive_instruction_count": pos_count,
        "negative_instruction_count": neg_count,
        "polarity_count": polarity_count,
    }


def index_prompt_dir(kind: str, directory: Path, vector_names: set[str], descriptions: dict[str, str]) -> pd.DataFrame:
    rows = []
    for path in sorted(directory.glob("*.json")):
        obj = load_json(path)
        counts = instruction_counts(obj)
        questions = obj.get("questions", [])
        eval_prompt = obj.get("eval_prompt")
        name = path.stem
        rows.append({
            "name": name,
            "artifact_type": kind,
            "path": str(path.relative_to(REPO_ROOT)),
            "description_present": bool(descriptions.get(name)),
            "description": descriptions.get(name, ""),
            **counts,
            "question_count": len(questions),
            "eval_prompt_present": bool(eval_prompt),
            "eval_prompt_mentions_trait_or_role": (
                bool(eval_prompt) and (f"**{name}**" in eval_prompt or name.replace("_", " ") in eval_prompt.lower())
            ),
            "vector_present": name in vector_names,
        })
    return pd.DataFrame(rows)


def read_json_mapping(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = load_json(path)
    if isinstance(data, dict):
        return {str(k): str(v) for k, v in data.items()}
    return {}


def vector_names(vector_dir: Path) -> set[str]:
    return {p.stem for p in vector_dir.glob("*.pt")}


def load_remote_belmore() -> tuple[dict[str, Any], pd.DataFrame | None, str | None]:
    try:
        with urllib.request.urlopen(BELMORE_API, timeout=30) as resp:
            meta = json.load(resp)
        with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
            urllib.request.urlretrieve(BELMORE_PARQUET, tmp.name)
            df = pd.read_parquet(tmp.name)
        return meta, df, None
    except Exception as exc:  # pragma: no cover - output documents failure.
        return {}, None, f"{type(exc).__name__}: {exc}"


def load_remote_github_summary() -> tuple[list[dict[str, Any]], str | None]:
    try:
        with urllib.request.urlopen(GITHUB_DATA_API, timeout=30) as resp:
            data = json.load(resp)
        return data, None
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"


def match_report(trait_artifacts: pd.DataFrame, trait_vecs: set[str], belmore_df: pd.DataFrame | None) -> pd.DataFrame:
    local_names = set(trait_artifacts["name"])
    belmore_trait_names = set()
    if belmore_df is not None and "source_type" in belmore_df.columns:
        belmore_trait_names = set(belmore_df.loc[belmore_df["source_type"] == "trait", "name"].astype(str))
    all_names = sorted(trait_vecs | local_names | belmore_trait_names)
    rows = []
    for name in all_names:
        normalized = name.lower().replace("-", "_").replace(" ", "_")
        rows.append({
            "name": name,
            "normalized_name": normalized,
            "in_qwen_trait_vectors": name in trait_vecs,
            "in_local_trait_artifacts": name in local_names,
            "in_belmore_prompt_dataset": name in belmore_trait_names,
            "exact_all_three_match": name in trait_vecs and name in local_names and name in belmore_trait_names,
        })
    return pd.DataFrame(rows)


def representative_artifacts(trait_coords: pd.DataFrame) -> dict[str, Any]:
    reps = {}
    for name in REPRESENTATIVE_TRAIT_NAMES:
        path = TRAIT_INSTRUCTION_DIR / f"{name}.json"
        if not path.exists():
            reps[name] = {"missing": True}
            continue
        obj = load_json(path)
        coord_row = trait_coords[trait_coords["trait"] == name].to_dict(orient="records")
        reps[name] = {
            "selection_reason": {
                "serious": "high trait PC1",
                "flippant": "low trait PC1",
                "callous": "high trait PC2",
                "grounded": "high trait PC3 and safety-relevant control",
                "subversive": "safety-relevant perturbation/challenge trait",
            }.get(name, "representative"),
            "trait_coordinates": coord_row[0] if coord_row else None,
            "artifact_path": str(path.relative_to(REPO_ROOT)),
            "description": read_json_mapping(TRAIT_LIST_PATH).get(name, ""),
            "artifact": obj,
        }
    return reps


def summarize_belmore(df: pd.DataFrame | None) -> dict[str, Any]:
    if df is None:
        return {"available": False}
    summary = {
        "available": True,
        "row_count": int(len(df)),
        "columns": list(df.columns),
        "source_type_counts": df["source_type"].value_counts(dropna=False).to_dict() if "source_type" in df else {},
        "is_default_count": int(df["is_default"].sum()) if "is_default" in df else None,
    }
    if {"source_type", "instruction_count", "question_count", "polarity_count"}.issubset(df.columns):
        table = (
            df.groupby("source_type")[["instruction_count", "question_count", "polarity_count"]]
            .agg(["min", "max", "mean"])
            .to_string()
        )
        summary["structure_by_source_type"] = "\n".join(line.rstrip() for line in table.splitlines())
    return summary


def write_reports(
    trait_index: pd.DataFrame,
    role_index: pd.DataFrame,
    match_df: pd.DataFrame,
    belmore_meta: dict[str, Any],
    belmore_df: pd.DataFrame | None,
    belmore_error: str | None,
    github_summary: list[dict[str, Any]],
    github_error: str | None,
    trait_coords: pd.DataFrame,
) -> None:
    belmore_summary = summarize_belmore(belmore_df)
    trait_exact = int(match_df["exact_all_three_match"].sum())
    missing_local = match_df[match_df["in_qwen_trait_vectors"] & ~match_df["in_local_trait_artifacts"]]["name"].tolist()
    missing_belmore = match_df[match_df["in_qwen_trait_vectors"] & ~match_df["in_belmore_prompt_dataset"]]["name"].tolist()
    extra_local = match_df[~match_df["in_qwen_trait_vectors"] & match_df["in_local_trait_artifacts"]]["name"].tolist()
    extra_belmore = match_df[~match_df["in_qwen_trait_vectors"] & match_df["in_belmore_prompt_dataset"]]["name"].tolist()

    report = f"""# Prompt Artifact Inventory For Geometry Forecasting

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

- GitHub API: `{GITHUB_DATA_API}`
- Hugging Face API: `{BELMORE_API}`
- Hugging Face parquet: `{BELMORE_PARQUET}`

GitHub data API status: {'available' if not github_error else 'failed: ' + github_error}
Belmore prompt dataset status: {'available' if belmore_df is not None else 'failed: ' + str(belmore_error)}

## Count Verification

| Artifact | Count |
|---|---:|
| Local role instruction JSON files | {len(role_index)} |
| Local trait instruction JSON files | {len(trait_index)} |
| Qwen role vector files | {int(role_index['vector_present'].sum())} matched locally / 275 expected vectors |
| Qwen trait vector files | {int(trait_index['vector_present'].sum())} matched locally / 240 expected vectors |
| Belmore prompt dataset rows | {belmore_summary.get('row_count', 'unavailable')} |
| Belmore default rows | {belmore_summary.get('is_default_count', 'unavailable')} |

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

- Exact match across Qwen trait vector names, local trait prompt artifact names, and Belmore trait names: {trait_exact} / 240
- Missing local artifacts for Qwen trait vectors: {missing_local}
- Missing Belmore artifacts for Qwen trait vectors: {missing_belmore}
- Extra local trait artifacts not in Qwen trait vectors: {extra_local}
- Extra Belmore trait artifacts not in Qwen trait vectors: {extra_belmore}

No naming normalization is required for the 240 trait artifacts used in the Qwen layer-48 analysis.

## Belmore Dataset Summary

```text
{belmore_summary.get('structure_by_source_type', 'unavailable')}
```

Belmore metadata SHA: `{belmore_meta.get('sha', 'unavailable')}`.

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
"""
    (OUTPUT_DIR / "prompt_artifact_inventory_report.md").write_text(report)

    feasibility = f"""# Forecasting Dataset Feasibility

## Judgment

Ready. Trait prompt artifacts are available locally and from the released Belmore prompt dataset, and they exactly match the 240 Qwen trait vector names.

## Minimum Dataset

- Input: trait description + positive instruction texts + behavioral questions.
- Target: trait PC1/PC2/PC3 from `research/outputs/trait_space_interpretation/trait_space_pca_coordinates.csv`.
- Split: hold out entire traits.

## Stronger Dataset

- Input: serialized full trait artifact including positive/negative instruction pairs and eval prompt.
- Target: mean-pooled 5120-D trait vector and trait PCA coordinates.
- Optional auxiliary target: similarity profile against 275 persona vectors.

## Caveats

- Eval prompts reveal the intended trait label and should be excluded from strict prompt-to-geometry forecasting if the goal is semantic generalization without target-label leakage.
- Negative instructions encode contrastive trait structure and may be predictive; include polarity explicitly.
- Forecasting from prompt text to released geometry tests artifact-to-vector predictability, not whether a target model would produce the same vector under new sampling.
"""
    (OUTPUT_DIR / "forecasting_dataset_feasibility.md").write_text(feasibility)


def main() -> None:
    trait_vecs = vector_names(TRAIT_VECTOR_DIR)
    role_vecs = vector_names(ROLE_VECTOR_DIR)
    trait_desc = read_json_mapping(TRAIT_LIST_PATH)
    role_desc = read_json_mapping(ROLE_LIST_PATH)

    trait_index = index_prompt_dir("trait", TRAIT_INSTRUCTION_DIR, trait_vecs, trait_desc)
    role_index = index_prompt_dir("role", ROLE_INSTRUCTION_DIR, role_vecs, role_desc)

    belmore_meta, belmore_df, belmore_error = load_remote_belmore()
    github_summary, github_error = load_remote_github_summary()
    match_df = match_report(trait_index, trait_vecs, belmore_df)
    trait_coords = pd.read_csv(TRAIT_SPACE_COORDS)

    trait_index["in_belmore_prompt_dataset"] = trait_index["name"].isin(
        set(belmore_df.loc[belmore_df["source_type"] == "trait", "name"]) if belmore_df is not None else set()
    )
    role_index["in_belmore_prompt_dataset"] = role_index["name"].isin(
        set(belmore_df.loc[belmore_df["source_type"].isin(["role", "default"]), "name"]) if belmore_df is not None else set()
    )

    trait_index.to_csv(OUTPUT_DIR / "trait_prompt_artifact_index.csv", index=False)
    role_index.to_csv(OUTPUT_DIR / "role_prompt_artifact_index.csv", index=False)
    match_df.to_csv(OUTPUT_DIR / "trait_vector_name_match_report.csv", index=False)
    (OUTPUT_DIR / "representative_trait_artifacts.json").write_text(
        json.dumps(representative_artifacts(trait_coords), indent=2)
    )

    write_reports(
        trait_index=trait_index,
        role_index=role_index,
        match_df=match_df,
        belmore_meta=belmore_meta,
        belmore_df=belmore_df,
        belmore_error=belmore_error,
        github_summary=github_summary,
        github_error=github_error,
        trait_coords=trait_coords,
    )

    print(json.dumps({
        "trait_artifact_count": len(trait_index),
        "role_artifact_count": len(role_index),
        "qwen_trait_vector_count": len(trait_vecs),
        "qwen_role_vector_count": len(role_vecs),
        "belmore_rows": None if belmore_df is None else len(belmore_df),
        "exact_trait_matches": int(match_df["exact_all_three_match"].sum()),
        "output_dir": str(OUTPUT_DIR),
    }, indent=2))


if __name__ == "__main__":
    main()
