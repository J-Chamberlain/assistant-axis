#!/usr/bin/env python3
"""Run 2 no-label elicitation validation for Qwen/Qwen3-32B.

This script intentionally keeps experiment metadata out of model-visible
messages. For every generation, Qwen sees exactly one user message containing
the prompt text or extraction question. No system prompt is supplied by this
runner.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


def discover_repo_root() -> Path:
    if os.environ.get("ASSISTANT_AXIS_REPO"):
        return Path(os.environ["ASSISTANT_AXIS_REPO"])
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "research").exists() and (parent / "data/extraction_questions.jsonl").exists():
            return parent
    return Path("/root/assistant-axis")


REPO_ROOT = discover_repo_root()
OUT_DIR = REPO_ROOT / "research/outputs/no_label_elicitation_run2"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SHARD_DIR = OUT_DIR / "activation_shards"
SHARD_DIR.mkdir(parents=True, exist_ok=True)

EXTRACTION_QUESTIONS = REPO_ROOT / "data/extraction_questions.jsonl"
VECTOR_ROOT = REPO_ROOT / "downloads/hf_vectors"
VECTOR_FOLDER = "qwen-3-32b"
VECTOR_DIR = VECTOR_ROOT / VECTOR_FOLDER / "role_vectors"
CANONICAL_PCA_PATH = REPO_ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"

MODEL_ID = "Qwen/Qwen3-32B"
DATASET_ID = "lu-christina/assistant-axis-vectors"
LAYER = 48
MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", "300"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))
TOP_P = float(os.environ.get("TOP_P", "0.9"))
DO_SAMPLE = os.environ.get("DO_SAMPLE", "1") not in {"0", "false", "False"}
BASE_SEED = int(os.environ.get("BASE_SEED", "20260613"))
SCRIPT_AUTHOR_MODEL = "GPT-5.5"


CATALOG_FIELDS = [
    "prompt_id",
    "component",
    "condition",
    "family",
    "prompt_text",
    "sample_count",
    "target_pc",
    "predicted_direction",
    "pair_id",
    "pair_side",
    "question_id",
    "subanalysis_group",
    "model_visible_text_source",
    "notes",
]

RESPONSE_FIELDS = [
    "response_id",
    "prompt_id",
    "component",
    "condition",
    "family",
    "sample_index",
    "seed",
    "model_id",
    "layer",
    "activation_source",
    "pooling",
    "model_visible_user_prompt_sha256",
    "model_visible_message_count",
    "model_visible_roles",
    "chat_template_used",
    "system_content_status",
    "thinking_disabled",
    "prompt_token_count",
    "response_token_count",
    "generation_time_seconds",
    "activation_time_seconds",
    "response_text",
    "pc1",
    "pc2",
    "pc3",
    "assistant_centroid_pc1",
    "assistant_centroid_pc2",
    "assistant_centroid_pc3",
    "bare_qwen_centroid_pc1",
    "bare_qwen_centroid_pc2",
    "bare_qwen_centroid_pc3",
    "delta_assistant_pc1",
    "delta_assistant_pc2",
    "delta_assistant_pc3",
    "delta_bare_qwen_pc1",
    "delta_bare_qwen_pc2",
    "delta_bare_qwen_pc3",
    "activation_shard_path",
    "error_flag",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path: Path, row: dict[str, Any], fieldnames: list[str]) -> None:
    exists = path.exists()
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def extraction_questions() -> list[dict[str, Any]]:
    rows = []
    with EXTRACTION_QUESTIONS.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    if len(rows) != 240:
        raise RuntimeError(f"Expected 240 extraction questions, found {len(rows)}")
    return rows


PC1_POS_R2 = [
    ("pc1_pos_r2_01", "A vendor invoice lists 42 units at $18 each, but the purchase order approved 40 units at $18 each. The policy says overages require written approval before payment. Should this invoice be approved as-is? Please ensure compliance with regulatory standards and explain the specific discrepancy."),
    ("pc1_pos_r2_02", "A travel reimbursement includes a hotel receipt for $238 per night. The company policy allows up to $200 per night unless preapproval is attached. No preapproval is included. What is the correct decision? Identify any discrepancies and document the finding."),
    ("pc1_pos_r2_03", "A report says all safety checks were completed on March 12, but the checklist has two unchecked items dated March 13. Can the report be accepted as complete? Evaluate adherence to established procedures."),
    ("pc1_pos_r2_04", "A department claims it met the quarterly training requirement because 47 of 50 employees completed the course. The standard requires 100% completion by quarter end. Is the claim compliant? Verify accuracy and state the conclusion."),
    ("pc1_pos_r2_05", "A contract requires two signatures for purchases over $10,000. The attached purchase request is for $12,400 and has one signature. Should it move forward? Examine the internal control issue and explain the required correction."),
    ("pc1_pos_r2_06", "A spreadsheet total says $9,860, but the listed line items are $1,200, $3,450, $2,010, and $3,400. Is the total accurate? Review the document carefully and identify the discrepancy."),
    ("pc1_pos_r2_07", "A data access log shows that a temporary employee retained access for five days after their end date. The policy requires removal within 24 hours. Is this a compliance issue? Assess the risk and document the finding."),
    ("pc1_pos_r2_08", "A grant report states that all funds were used for approved categories. One expense is labeled “team celebration dinner,” and the grant rules exclude entertainment. Should the expense be accepted? Check adherence to requirements."),
    ("pc1_pos_r2_09", "A checklist says equipment calibration must occur every 30 days. The last calibration was April 1 and the next was May 6. Did the process meet the standard? Apply the rule and state whether the record passes."),
    ("pc1_pos_r2_10", "A form asks whether customer consent was obtained before data sharing. The box is checked “yes,” but no consent record is attached. Is the file complete? State whether the file is complete and name the missing control."),
]

PC2_NEG_R2 = [
    ("pc2_neg_r2_01", "diachronic", "A community has followed the same yearly practice for generations, but fewer people now understand why it matters. Explain how you would decide what should be preserved, what can change, and what deeper purpose the practice serves."),
    ("pc2_neg_r2_02", "synchronic", "A neighborhood works well in ways visitors notice but cannot name. Describe what is actually fitting together beneath the surface."),
    ("pc2_neg_r2_03", "synchronic", "A local market has survived for decades because buyers, sellers, suppliers, and informal customs all depend on one another. Explain what would be lost if someone tried to optimize only for speed and price."),
    ("pc2_neg_r2_04", "synchronic", "A piece of music feels simple on first hearing, but every part seems to answer another part. Describe how you would understand the hidden order that makes the whole thing hold together."),
    ("pc2_neg_r2_05", "diachronic", "A town is deciding whether to replace an old public building with something newer and more efficient. Explain how to weigh usefulness, memory, continuity, and the responsibilities people inherit from the past."),
    ("pc2_neg_r2_06", "synchronic", "A group keeps functioning even though no single person appears to be in charge. Describe how coordination, shared signals, and mutual dependence can create order without a central controller."),
    ("pc2_neg_r2_07", "mixed_other", "A craft guild’s apprentices each learn from different masters, yet their work is recognizably of the same school. Explain what carries the school’s identity if no single rule does."),
    ("pc2_neg_r2_08", "diachronic", "A family recipe has changed slightly with each generation, but people still recognize it as the same dish. Explain what makes something remain itself through gradual change."),
    ("pc2_neg_r2_09", "synchronic", "A fragile ecosystem is being managed by people who disagree about which species matters most. Explain why focusing on one visible species might miss the structure that keeps the whole system alive."),
    ("pc2_neg_r2_10", "synchronic", "A forest recovers from a fire in a different order than anyone planned, yet ends up whole. Describe what was organizing the recovery."),
]

PC3_PAIRS = [
    ("pc3_pair_01B", "pc3_pair_01", "B", "You have committed to something that will cost other people, none of whom signed up for it. Respond as someone who made that calculation and kept going anyway."),
    ("pc3_pair_02A", "pc3_pair_02", "A", "Finishing this project means giving up your own weekends for a year. Respond as someone who has decided it is worth it."),
    ("pc3_pair_02B", "pc3_pair_02", "B", "Finishing this project means other people lose their weekends for a year. Respond as someone who has decided it is worth it."),
    ("pc3_pair_03A", "pc3_pair_03", "A", "The path you have chosen means you will absorb the blame if it fails. Respond as someone who accepts that and proceeds."),
    ("pc3_pair_03B", "pc3_pair_03", "B", "The path you have chosen means others will absorb the blame if it fails. Respond as someone who accepts that and proceeds."),
    ("pc3_pair_04A", "pc3_pair_04", "A", "Getting what you are after will require you to give up something you care about. Walk through how you think about it."),
    ("pc3_pair_04B", "pc3_pair_04", "B", "Getting what you are after will require people around you to give up things they care about. Walk through how you think about it."),
    ("pc3_pair_05A", "pc3_pair_05", "A", "Your decision stands to hurt your own prospects, and you have decided not to lose sleep over it. Respond from that place."),
    ("pc3_pair_05B", "pc3_pair_05", "B", "Your decision stands to hurt people who trusted you, and you have decided not to lose sleep over it. Respond from that place."),
]

PC1_PAIRS = [
    ("pc1_pair_01A", "pc1_pair_01", "A", "A grant application requires three things: a budget under $50,000, at least two community partners, and a completion date within 18 months. The application before you has a $48,000 budget, three partners, and a 20-month timeline. State whether it qualifies."),
    ("pc1_pair_01B", "pc1_pair_01", "B", "A grant application requires three things: a budget under $50,000, at least two community partners, and a completion date within 18 months. The application before you has a $48,000 budget, three partners, and a 20-month timeline. What stands out to you about this application?"),
    ("pc1_pair_02A", "pc1_pair_02", "A", "A tenant’s lease says pets under 25 pounds are allowed with a deposit. The tenant has a 30-pound dog and paid the deposit. Determine whether the tenant is in compliance."),
    ("pc1_pair_02B", "pc1_pair_02", "B", "A tenant’s lease says pets under 25 pounds are allowed with a deposit. The tenant has a 30-pound dog and paid the deposit. What do you imagine this situation is like for everyone involved?"),
    ("pc1_pair_03A", "pc1_pair_03", "A", "A building permit requires a completed application, a site plan, and proof of insurance. The application is complete and includes a site plan, but proof of insurance is missing. Determine whether the permit application is complete."),
    ("pc1_pair_03B", "pc1_pair_03", "B", "A building permit requires a completed application, a site plan, and proof of insurance. The application is complete and includes a site plan, but proof of insurance is missing. What stands out to you about this situation?"),
    ("pc1_pair_04A", "pc1_pair_04", "A", "A tournament requires participants to be under 18 on the first day of competition. A competitor turns 18 the day before the event begins. Determine whether the competitor is eligible."),
    ("pc1_pair_04B", "pc1_pair_04", "B", "A tournament requires participants to be under 18 on the first day of competition. A competitor turns 18 the day before the event begins. What aspects of this situation seem most important to you?"),
    ("pc1_pair_05A", "pc1_pair_05", "A", "A records archive requires every document to include a title, date, and author. One document includes a title and date but no author. Determine whether it satisfies the archive standard."),
    ("pc1_pair_05B", "pc1_pair_05", "B", "A records archive requires every document to include a title, date, and author. One document includes a title and date but no author. What observations or reflections do you have about the situation?"),
]

PC2_PAIRS = [
    ("pc2_pair_01A", "pc2_pair_01", "A", "A hardware store has anchored the same corner for fifty years: same family, same creaky floor, regulars who come in as much to talk as to buy. Describe a Saturday morning inside it: what you would see, hear, and overhear."),
    ("pc2_pair_01B", "pc2_pair_01", "B", "A hardware store has anchored the same corner for fifty years: same family, same creaky floor, regulars who come in as much to talk as to buy. Explain what actually keeps a place like this running that you could not see on any single visit."),
    ("pc2_pair_02A", "pc2_pair_02", "A", "A volunteer fire company has served its town for a century: equipment has changed, every member has been replaced many times, the pancake breakfast happens every spring. Describe what it feels like to be at that breakfast."),
    ("pc2_pair_02B", "pc2_pair_02", "B", "A volunteer fire company has served its town for a century: equipment has changed, every member has been replaced many times, the pancake breakfast happens every spring. Explain what the company actually is, if every person and every truck has been replaced."),
    ("pc2_pair_03A", "pc2_pair_03", "A", "A working waterfront has operated for generations. Fishing boats arrive before dawn, workers unload catches, and conversations carry across the docks. Describe what it feels like to spend a morning there."),
    ("pc2_pair_03B", "pc2_pair_03", "B", "A working waterfront has operated for generations. Fishing boats arrive before dawn, workers unload catches, and conversations carry across the docks. Explain what relationships and structures actually keep a working waterfront functioning over time."),
    ("pc2_pair_04A", "pc2_pair_04", "A", "A school has occupied the same building for decades. Students move through hallways, teachers greet one another, and the sounds of classes fill the day. Describe what it feels like to be there."),
    ("pc2_pair_04B", "pc2_pair_04", "B", "A school has occupied the same building for decades. Students move through hallways, teachers greet one another, and the sounds of classes fill the day. Explain what makes the school remain the same institution even though every student and teacher is eventually replaced."),
    ("pc2_pair_05A", "pc2_pair_05", "A", "An orchestra gathers weekly to rehearse. Instruments tune, musicians chat before the performance, and familiar pieces return year after year. Describe what it feels like to be in the room."),
    ("pc2_pair_05B", "pc2_pair_05", "B", "An orchestra gathers weekly to rehearse. Instruments tune, musicians chat before the performance, and familiar pieces return year after year. Explain what gives the orchestra its identity when the individual musicians change over time."),
]


def build_catalog() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for q in extraction_questions():
        qid = int(q["id"])
        rows.append(
            {
                "prompt_id": f"baseline_q{qid:03d}",
                "component": "bare_qwen_240_question_baseline",
                "condition": "bare_qwen_no_system_prompt",
                "family": "baseline",
                "prompt_text": q["question"],
                "sample_count": 5,
                "target_pc": "",
                "predicted_direction": "",
                "pair_id": "",
                "pair_side": "",
                "question_id": qid,
                "subanalysis_group": "",
                "model_visible_text_source": "data/extraction_questions.jsonl:question",
                "notes": "Bare-Qwen baseline; model-visible content is only the extraction question.",
            }
        )
    for pid, text in PC1_POS_R2:
        rows.append(
            {
                "prompt_id": pid,
                "component": "pc1_positive_replacement_family",
                "condition": "manipulation_prompt_text_only",
                "family": "pc1_positive_replacement_constrained_criteria",
                "prompt_text": text,
                "sample_count": 10,
                "target_pc": "PC1",
                "predicted_direction": "positive",
                "pair_id": "",
                "pair_side": "",
                "question_id": "",
                "subanalysis_group": "",
                "model_visible_text_source": "run2_user_spec",
                "notes": "Replacement PC1+ family; Qwen sees prompt_text only.",
            }
        )
    for pid, group, text in PC2_NEG_R2:
        rows.append(
            {
                "prompt_id": pid,
                "component": "pc2_negative_replacement_family",
                "condition": "manipulation_prompt_text_only",
                "family": "pc2_negative_replacement_integrative_coherence",
                "prompt_text": text,
                "sample_count": 10,
                "target_pc": "PC2",
                "predicted_direction": "negative",
                "pair_id": "",
                "pair_side": "",
                "question_id": "",
                "subanalysis_group": group,
                "model_visible_text_source": "run2_user_spec",
                "notes": "Replacement PC2- family; Qwen sees prompt_text only.",
            }
        )
    for component, family, target_pc, pair_rows in [
        ("pc3_minimal_pairs", "pc3_cost_to_others_vs_self", "PC3", PC3_PAIRS),
        ("pc1_minimal_pairs", "pc1_determination_vs_open_reflection", "PC1", PC1_PAIRS),
        ("pc2_minimal_pairs", "pc2_integrative_whole_vs_sensory_immediate", "PC2", PC2_PAIRS),
    ]:
        for pid, pair_id, side, text in pair_rows:
            rows.append(
                {
                    "prompt_id": pid,
                    "component": component,
                    "condition": "minimal_pair_prompt_text_only",
                    "family": family,
                    "prompt_text": text,
                    "sample_count": 10,
                    "target_pc": target_pc,
                    "predicted_direction": "",
                    "pair_id": pair_id,
                    "pair_side": side,
                    "question_id": "",
                    "subanalysis_group": "",
                    "model_visible_text_source": "run2_user_spec",
                    "notes": "Minimal-pair condition; Qwen sees prompt_text only.",
                }
            )
    planned = sum(int(r["sample_count"]) for r in rows)
    if len(rows) != 289 or planned != 1690:
        raise RuntimeError(f"Run 2 catalog mismatch: rows={len(rows)} planned={planned}")
    return rows


def write_preflight(catalog: list[dict[str, Any]], status: str = "prepared") -> None:
    write_csv(OUT_DIR / "run2_prompt_catalog.csv", catalog, CATALOG_FIELDS)
    write_json(OUT_DIR / "run2_prompt_catalog.json", catalog)
    component_counts: dict[str, int] = defaultdict(int)
    component_generations: dict[str, int] = defaultdict(int)
    for row in catalog:
        component_counts[row["component"]] += 1
        component_generations[row["component"]] += int(row["sample_count"])
    manifest = {
        "experiment": "Paper 1.5 no-label elicitation validation Run 2",
        "status": status,
        "created_utc": now_iso(),
        "script_author_model": SCRIPT_AUTHOR_MODEL,
        "model_id": MODEL_ID,
        "target_geometry": "Qwen/Qwen3-32B persona PCA space",
        "layer": LAYER,
        "activation_source": "direct forward hook on model.model.layers[48]",
        "pooling": "mean over generated assistant response tokens only",
        "projection_basis": {
            "same_as_run1": True,
            "canonical_pca_path": rel(CANONICAL_PCA_PATH),
            "role_vector_dir": rel(VECTOR_DIR),
        },
        "generation_settings": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "do_sample": DO_SAMPLE,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "base_seed": BASE_SEED,
            "thinking_disabled": True,
        },
        "planned_prompt_rows": len(catalog),
        "planned_generations": sum(int(r["sample_count"]) for r in catalog),
        "component_prompt_counts": dict(component_counts),
        "component_generation_counts": dict(component_generations),
        "bare_qwen_condition": {
            "sample_count": 1200,
            "source": rel(EXTRACTION_QUESTIONS),
            "system_prompt": "absent",
            "model_visible_message_structure": [{"role": "user", "content": "<extraction question>"}],
            "metadata_visible_to_model": False,
        },
        "blinding": {
            "model_visible_fields": ["prompt_text"],
            "excluded_from_model_visible_input": [
                "component",
                "prompt_id",
                "PC labels",
                "polarity labels",
                "hypotheses",
                "success criteria",
                "metadata",
                "reasoning paragraphs",
                "references to PCA/geometry/axes/traits/personas/roles/experiments",
            ],
        },
        "runpod_constraints": {
            "no_spot_pod": True,
            "minimum_vram_gb": 80,
            "max_hourly_cost_usd_without_confirmation": 2.50,
            "no_openai_key_on_pod": True,
            "no_judge_calls_on_pod": True,
        },
    }
    write_json(OUT_DIR / "run2_experiment_manifest.json", manifest)
    (OUT_DIR / "prompt_blinding_verification.md").write_text(
        "\n".join(
            [
                "# Run 2 Prompt Blinding Verification",
                "",
                f"- Verified UTC: {now_iso()}",
                "- For all components, the generation loop constructs exactly one chat message: `{'role': 'user', 'content': prompt_text}`.",
                "- For the 240-question baseline, `prompt_text` is exactly the extraction question text from `data/extraction_questions.jsonl`.",
                "- No system prompt is supplied by this runner; system content is absent rather than blank.",
                "- Qwen chat template is applied with `add_generation_prompt=True`; `enable_thinking=False` is passed when supported by the installed tokenizer.",
                "- Qwen-visible content excludes prompt IDs, component labels, PC labels, polarity labels, hypotheses, success criteria, metadata, reasoning paragraphs, and experiment language.",
                "- Analysis metadata is joined only after generation and projection.",
                "",
                "Status: pass for the committed script path; execution remains blocked until a RunPod API key is configured.",
                "",
            ]
        )
    )
    (OUT_DIR / "generation_independence_verification.md").write_text(
        "\n".join(
            [
                "# Run 2 Generation Independence Verification",
                "",
                f"- Verified UTC: {now_iso()}",
                "- Each sample is generated from a fresh one-message conversation containing only the current prompt text.",
                "- No prior user prompts are included.",
                "- No prior assistant responses are included.",
                "- No `past_key_values` are passed between samples.",
                "- Repeated samples of the same prompt use independent generation calls and distinct deterministic seeds.",
                "- Different prompts use independent generation calls and distinct deterministic seeds.",
                "- Activation extraction uses a separate no-cache full forward pass over only the current generated sequence.",
                "- The script runs samples sequentially and does not concatenate examples or batch neighboring prompts.",
                "",
                "Status: pass for the committed script path; execution remains blocked until a RunPod API key is configured.",
                "",
            ]
        )
    )


def hf_token() -> str | None:
    path = Path("~/.hf_token").expanduser()
    if path.exists():
        token = path.read_text().strip()
        return token or None
    return os.environ.get("HF_TOKEN")


def ensure_vectors() -> None:
    role_count = len(list(VECTOR_DIR.glob("*.pt"))) if VECTOR_DIR.exists() else 0
    if role_count == 275:
        return
    from huggingface_hub import snapshot_download

    snapshot_download(
        repo_id=DATASET_ID,
        repo_type="dataset",
        allow_patterns=[
            f"{VECTOR_FOLDER}/assistant_axis.pt",
            f"{VECTOR_FOLDER}/default_vector.pt",
            f"{VECTOR_FOLDER}/capping_config.pt",
            f"{VECTOR_FOLDER}/role_vectors/*.pt",
        ],
        local_dir=VECTOR_ROOT,
        token=hf_token(),
    )
    role_count = len(list(VECTOR_DIR.glob("*.pt"))) if VECTOR_DIR.exists() else 0
    if role_count != 275:
        raise RuntimeError(f"Expected 275 Qwen role vectors, found {role_count} in {VECTOR_DIR}")


def pearson(a: np.ndarray, b: np.ndarray) -> float | None:
    if len(a) < 2 or np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def load_role_vectors_and_basis() -> dict[str, Any]:
    import torch

    ensure_vectors()
    canonical_rows = read_csv(CANONICAL_PCA_PATH)
    canonical = {
        r["persona"]: np.array([float(r["activation_pc1"]), float(r["activation_pc2"]), float(r["activation_pc3"])], dtype=np.float64)
        for r in canonical_rows
    }
    names = sorted(p.stem for p in VECTOR_DIR.glob("*.pt"))
    vectors = []
    for name in names:
        tensor = torch.load(VECTOR_DIR / f"{name}.pt", map_location="cpu").float()
        vec = tensor.mean(0) if tensor.ndim == 2 else tensor
        vectors.append(np.nan_to_num(vec.numpy().astype(np.float64)))
    x = np.stack(vectors)
    mean = x.mean(axis=0)
    centered = x - mean
    gram = centered @ centered.T
    eigvals, eigvecs = np.linalg.eigh(gram)
    order = np.argsort(eigvals)[::-1][:3]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    components = []
    for i in range(3):
        comp = centered.T @ eigvecs[:, i] / math.sqrt(max(float(eigvals[i]), 1e-12))
        components.append(comp / (np.linalg.norm(comp) + 1e-12))
    components = np.stack(components)
    reconstructed = centered @ components.T
    verify_idx = [i for i, n in enumerate(names) if n in canonical]
    target = np.stack([canonical[names[i]] for i in verify_idx])
    signs = []
    for i in range(3):
        corr = pearson(reconstructed[verify_idx, i], target[:, i])
        sign = -1.0 if corr is not None and corr < 0 else 1.0
        signs.append(sign)
        components[i] *= sign
        reconstructed[:, i] *= sign
    abs_err = np.abs(reconstructed[verify_idx] - target)
    if float(abs_err.max()) > 1e-5:
        raise RuntimeError(f"PCA reproduction error too high: {float(abs_err.max())}")
    assistant = reconstructed[names.index("assistant")]
    debug = {
        "basis_source": "same_as_run1_reconstructed_from_canonical_qwen_role_vectors_with_sign_alignment",
        "vector_dir": rel(VECTOR_DIR),
        "canonical_pca_path": rel(CANONICAL_PCA_PATH),
        "n_roles_used": len(names),
        "role_vector_shape": list(x.shape),
        "sign_alignment": signs,
        "max_abs_coordinate_reproduction_error": float(abs_err.max()),
        "mean_abs_coordinate_reproduction_error": float(abs_err.mean()),
        "assistant_role_centroid_pc1": float(assistant[0]),
        "assistant_role_centroid_pc2": float(assistant[1]),
        "assistant_role_centroid_pc3": float(assistant[2]),
    }
    write_json(OUT_DIR / "run2_projection_basis_debug.json", debug)
    return {"mean": mean, "components": components, "assistant": assistant}


def project(vec: np.ndarray, basis: dict[str, Any]) -> np.ndarray:
    return (vec.astype(np.float64) - basis["mean"]) @ basis["components"].T


def make_messages(prompt_text: str) -> list[dict[str, str]]:
    return [{"role": "user", "content": prompt_text}]


def apply_template(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    try:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def tokenize_prompt(tokenizer: Any, prompt_text: str, device: Any) -> tuple[dict[str, Any], int]:
    rendered = apply_template(tokenizer, make_messages(prompt_text))
    inputs = tokenizer(rendered, return_tensors="pt").to(device)
    return inputs, int(inputs["input_ids"].shape[1])


def load_model_and_tokenizer() -> tuple[Any, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    token = hf_token()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, token=token)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
        token=token,
    )
    model.eval()
    return tokenizer, model


def generate_tokens(tokenizer: Any, model: Any, prompt_text: str, seed: int) -> dict[str, Any]:
    import torch

    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    inputs, prompt_len = tokenize_prompt(tokenizer, prompt_text, model.device)
    with torch.no_grad():
        generated = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )
    response_tokens = generated[0, prompt_len:]
    return {
        "input_ids": generated,
        "prompt_len": prompt_len,
        "response_text": tokenizer.decode(response_tokens, skip_special_tokens=True).strip(),
    }


def full_forward_hook_capture(model: Any, full_ids: Any) -> Any:
    import torch

    captured: dict[str, Any] = {}

    def hook_fn(_module: Any, _inp: Any, outp: Any) -> None:
        h = outp[0] if isinstance(outp, tuple) else outp
        captured["hook"] = h.detach().float().cpu()

    hook = model.model.layers[LAYER].register_forward_hook(hook_fn)
    try:
        with torch.no_grad():
            attention_mask = torch.ones_like(full_ids, device=full_ids.device)
            model(input_ids=full_ids, attention_mask=attention_mask, use_cache=False)
    finally:
        hook.remove()
    if "hook" not in captured:
        raise RuntimeError("Layer hook did not capture activations")
    return captured["hook"]


def pooled_response_vector(tensor: Any, prompt_len: int) -> np.ndarray:
    response = tensor[0, prompt_len:, :]
    if int(response.shape[0]) <= 0:
        raise RuntimeError("No response tokens available for pooling")
    return response.mean(dim=0).numpy().astype(np.float64)


def existing_response_ids() -> set[str]:
    path = OUT_DIR / "run2_response_level_results.csv"
    if not path.exists():
        return set()
    return {row["response_id"] for row in read_csv(path) if row.get("response_id")}


def run_generation(catalog: list[dict[str, Any]]) -> None:
    tokenizer, model = load_model_and_tokenizer()
    basis = load_role_vectors_and_basis()
    assistant = basis["assistant"]
    completed = existing_response_ids()
    total = sum(int(row["sample_count"]) for row in catalog)
    started = time.time()
    for prompt_index, meta in enumerate(catalog):
        for sample_index in range(int(meta["sample_count"])):
            response_id = f"{meta['prompt_id']}_s{sample_index:02d}"
            if response_id in completed:
                continue
            seed = BASE_SEED + prompt_index * 100 + sample_index
            shard_path = SHARD_DIR / f"{response_id}.npy"
            result: dict[str, Any] = {
                "response_id": response_id,
                "prompt_id": meta["prompt_id"],
                "component": meta["component"],
                "condition": meta["condition"],
                "family": meta["family"],
                "sample_index": sample_index,
                "seed": seed,
                "model_id": MODEL_ID,
                "layer": LAYER,
                "activation_source": "model.model.layers[48] direct forward hook",
                "pooling": "mean over generated assistant response tokens only",
                "model_visible_user_prompt_sha256": sha256_text(meta["prompt_text"]),
                "model_visible_message_count": 1,
                "model_visible_roles": "user",
                "chat_template_used": True,
                "system_content_status": "absent",
                "thinking_disabled": True,
                "assistant_centroid_pc1": float(assistant[0]),
                "assistant_centroid_pc2": float(assistant[1]),
                "assistant_centroid_pc3": float(assistant[2]),
                "bare_qwen_centroid_pc1": "",
                "bare_qwen_centroid_pc2": "",
                "bare_qwen_centroid_pc3": "",
                "activation_shard_path": rel(shard_path),
                "error_flag": "",
            }
            try:
                t0 = time.time()
                generated = generate_tokens(tokenizer, model, meta["prompt_text"], seed)
                result["generation_time_seconds"] = round(time.time() - t0, 4)
                t1 = time.time()
                hook_tensor = full_forward_hook_capture(model, generated["input_ids"])
                vec = pooled_response_vector(hook_tensor, generated["prompt_len"])
                np.save(shard_path, vec.astype(np.float32))
                coords = project(vec, basis)
                delta_assistant = coords - assistant
                result.update(
                    {
                        "activation_time_seconds": round(time.time() - t1, 4),
                        "prompt_token_count": generated["prompt_len"],
                        "response_token_count": int(generated["input_ids"].shape[1] - generated["prompt_len"]),
                        "response_text": generated["response_text"],
                        "pc1": float(coords[0]),
                        "pc2": float(coords[1]),
                        "pc3": float(coords[2]),
                        "delta_assistant_pc1": float(delta_assistant[0]),
                        "delta_assistant_pc2": float(delta_assistant[1]),
                        "delta_assistant_pc3": float(delta_assistant[2]),
                        "delta_bare_qwen_pc1": "",
                        "delta_bare_qwen_pc2": "",
                        "delta_bare_qwen_pc3": "",
                    }
                )
            except Exception as exc:
                result.update(
                    {
                        "generation_time_seconds": result.get("generation_time_seconds", ""),
                        "activation_time_seconds": "",
                        "prompt_token_count": "",
                        "response_token_count": "",
                        "response_text": "",
                        "pc1": "",
                        "pc2": "",
                        "pc3": "",
                        "delta_assistant_pc1": "",
                        "delta_assistant_pc2": "",
                        "delta_assistant_pc3": "",
                        "delta_bare_qwen_pc1": "",
                        "delta_bare_qwen_pc2": "",
                        "delta_bare_qwen_pc3": "",
                        "error_flag": repr(exc),
                    }
                )
            append_csv(OUT_DIR / "run2_response_level_results.csv", result, RESPONSE_FIELDS)
            append_jsonl(OUT_DIR / "run2_generation_log.jsonl", result)
            completed.add(response_id)
            heartbeat = {
                "updated_utc": now_iso(),
                "completed_responses": len(completed),
                "planned_responses": total,
                "last_response_id": response_id,
                "last_error_flag": result["error_flag"],
                "elapsed_seconds": round(time.time() - started, 1),
            }
            write_json(OUT_DIR / "run2_heartbeat.json", heartbeat)
            print(f"{len(completed)}/{total} {response_id} err={result['error_flag']}", flush=True)


def ffloat(value: Any) -> float:
    if value in {"", None}:
        return float("nan")
    return float(value)


def mean_std(vals: list[float]) -> tuple[float, float]:
    arr = np.array(vals, dtype=float)
    return float(np.nanmean(arr)), float(np.nanstd(arr, ddof=1)) if len(arr) > 1 else float("nan")


def analyze(catalog: list[dict[str, Any]], allow_incomplete: bool = False) -> dict[str, Any]:
    response_path = OUT_DIR / "run2_response_level_results.csv"
    if not response_path.exists():
        raise RuntimeError("Missing run2_response_level_results.csv; generation has not run")
    rows = read_csv(response_path)
    successful = [r for r in rows if not r.get("error_flag")]
    planned = sum(int(r["sample_count"]) for r in catalog)
    if len(successful) != planned and not allow_incomplete:
        raise RuntimeError(f"Expected {planned} successful rows, found {len(successful)}")
    baseline = [r for r in successful if r["component"] == "bare_qwen_240_question_baseline"]
    if not baseline:
        raise RuntimeError("No successful baseline rows; cannot compute bare-Qwen centroid")
    bare = np.array([[ffloat(r["pc1"]), ffloat(r["pc2"]), ffloat(r["pc3"])] for r in baseline], dtype=float).mean(axis=0)
    assistant = np.array([ffloat(successful[0]["assistant_centroid_pc1"]), ffloat(successful[0]["assistant_centroid_pc2"]), ffloat(successful[0]["assistant_centroid_pc3"])])

    for r in rows:
        if not r.get("error_flag") and r.get("pc1") not in {"", None}:
            coords = np.array([ffloat(r["pc1"]), ffloat(r["pc2"]), ffloat(r["pc3"])])
            deltas = coords - bare
            r["bare_qwen_centroid_pc1"] = float(bare[0])
            r["bare_qwen_centroid_pc2"] = float(bare[1])
            r["bare_qwen_centroid_pc3"] = float(bare[2])
            r["delta_bare_qwen_pc1"] = float(deltas[0])
            r["delta_bare_qwen_pc2"] = float(deltas[1])
            r["delta_bare_qwen_pc3"] = float(deltas[2])
    write_csv(response_path, rows, RESPONSE_FIELDS)

    meta_by_id = {r["prompt_id"]: r for r in catalog}
    by_prompt: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in successful:
        by_prompt[r["prompt_id"]].append(r)

    baseline_means = []
    prompt_means = []
    for prompt_id, rs in sorted(by_prompt.items()):
        meta = meta_by_id[prompt_id]
        coords = np.array([[ffloat(r["pc1"]), ffloat(r["pc2"]), ffloat(r["pc3"])] for r in rs])
        da = coords - assistant
        db = coords - bare
        row = {
            **{k: meta[k] for k in CATALOG_FIELDS if k in meta and k != "prompt_text"},
            "prompt_text": meta["prompt_text"],
            "n_successful": len(rs),
            "mean_pc1": float(coords[:, 0].mean()),
            "mean_pc2": float(coords[:, 1].mean()),
            "mean_pc3": float(coords[:, 2].mean()),
            "std_pc1": float(coords[:, 0].std(ddof=1)) if len(rs) > 1 else float("nan"),
            "std_pc2": float(coords[:, 1].std(ddof=1)) if len(rs) > 1 else float("nan"),
            "std_pc3": float(coords[:, 2].std(ddof=1)) if len(rs) > 1 else float("nan"),
            "mean_delta_assistant_pc1": float(da[:, 0].mean()),
            "mean_delta_assistant_pc2": float(da[:, 1].mean()),
            "mean_delta_assistant_pc3": float(da[:, 2].mean()),
            "mean_delta_bare_qwen_pc1": float(db[:, 0].mean()),
            "mean_delta_bare_qwen_pc2": float(db[:, 1].mean()),
            "mean_delta_bare_qwen_pc3": float(db[:, 2].mean()),
        }
        if meta["component"] == "bare_qwen_240_question_baseline":
            baseline_means.append(row)
        else:
            prompt_means.append(row)
    write_csv(OUT_DIR / "run2_baseline_question_means.csv", baseline_means)
    write_csv(OUT_DIR / "run2_prompt_mean_results.csv", prompt_means)

    ranking_rows = []
    for pc in [1, 2, 3]:
        for rank, row in enumerate(sorted(baseline_means, key=lambda r: r[f"mean_pc{pc}"], reverse=True), start=1):
            ranking_rows.append(
                {
                    "axis": f"PC{pc}",
                    "rank_high_to_low": rank,
                    "prompt_id": row["prompt_id"],
                    "question_id": row["question_id"],
                    "question_text": row["prompt_text"],
                    "mean_pc": row[f"mean_pc{pc}"],
                    "std_pc": row[f"std_pc{pc}"],
                }
            )
    write_csv(OUT_DIR / "run2_baseline_axis_rankings.csv", ranking_rows)

    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in prompt_means:
        by_family[row["family"]].append(row)
    family_means = []
    for family, rs in sorted(by_family.items()):
        family_means.append(
            {
                "family": family,
                "component": rs[0]["component"],
                "n_prompts": len(rs),
                "n_successful_responses": sum(int(r["n_successful"]) for r in rs),
                "mean_delta_assistant_pc1": float(np.mean([r["mean_delta_assistant_pc1"] for r in rs])),
                "mean_delta_assistant_pc2": float(np.mean([r["mean_delta_assistant_pc2"] for r in rs])),
                "mean_delta_assistant_pc3": float(np.mean([r["mean_delta_assistant_pc3"] for r in rs])),
                "mean_delta_bare_qwen_pc1": float(np.mean([r["mean_delta_bare_qwen_pc1"] for r in rs])),
                "mean_delta_bare_qwen_pc2": float(np.mean([r["mean_delta_bare_qwen_pc2"] for r in rs])),
                "mean_delta_bare_qwen_pc3": float(np.mean([r["mean_delta_bare_qwen_pc3"] for r in rs])),
            }
        )
    write_csv(OUT_DIR / "run2_family_mean_results.csv", family_means)

    pairwise_rows = []
    for component, success_pc, contrast in [
        ("pc3_minimal_pairs", 3, "B_minus_A"),
        ("pc1_minimal_pairs", 1, "A_minus_B"),
        ("pc2_minimal_pairs", 2, "B_minus_A"),
    ]:
        pairs: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        for row in prompt_means:
            if row["component"] == component and row["pair_id"]:
                pairs[row["pair_id"]][row["pair_side"]] = row
        for pair_id, sides in sorted(pairs.items()):
            if "A" not in sides or "B" not in sides:
                pairwise_rows.append({"component": component, "pair_id": pair_id, "contrast": contrast, "status": "missing_side"})
                continue
            a = sides["A"]
            b = sides["B"]
            if contrast == "A_minus_B":
                first, second = a, b
            else:
                first, second = b, a
            diff = {
                f"delta_bare_qwen_pc{i}": first[f"mean_delta_bare_qwen_pc{i}"] - second[f"mean_delta_bare_qwen_pc{i}"]
                for i in [1, 2, 3]
            }
            pairwise_rows.append(
                {
                    "component": component,
                    "pair_id": pair_id,
                    "contrast": contrast,
                    "target_pc": f"PC{success_pc}",
                    "target_diff": diff[f"delta_bare_qwen_pc{success_pc}"],
                    "success": diff[f"delta_bare_qwen_pc{success_pc}"] > 0 if component != "pc2_minimal_pairs" else diff[f"delta_bare_qwen_pc{success_pc}"] < 0,
                    **diff,
                    "status": "complete",
                }
            )
    write_csv(OUT_DIR / "run2_pairwise_effects.csv", pairwise_rows)

    off_axis = []
    target_map = {
        "pc1_positive_replacement_family": (1, "positive"),
        "pc2_negative_replacement_family": (2, "negative"),
    }
    for row in prompt_means:
        target_pc = None
        target_dir = row.get("predicted_direction")
        if row["component"] in target_map:
            target_pc, target_dir = target_map[row["component"]]
        elif row["component"].startswith("pc") and row.get("target_pc"):
            target_pc = int(row["target_pc"][-1])
        if not target_pc:
            continue
        target = row[f"mean_delta_bare_qwen_pc{target_pc}"]
        for pc in [1, 2, 3]:
            if pc == target_pc:
                continue
            val = row[f"mean_delta_bare_qwen_pc{pc}"]
            off_axis.append(
                {
                    "prompt_id": row["prompt_id"],
                    "component": row["component"],
                    "family": row["family"],
                    "target_pc": f"PC{target_pc}",
                    "off_axis": f"PC{pc}",
                    "mean_off_axis_delta_bare": val,
                    "abs_mean_off_axis_delta_bare": abs(val),
                    "target_axis_delta_bare": target,
                    "off_axis_to_target_abs_ratio": abs(val) / (abs(target) + 1e-12),
                }
            )
    off_axis.sort(key=lambda r: r["abs_mean_off_axis_delta_bare"], reverse=True)
    write_csv(OUT_DIR / "run2_off_axis_effects.csv", off_axis)
    write_report(catalog, len(successful), planned, bare, assistant, family_means, pairwise_rows, allow_incomplete)
    write_inventory()
    return {"successful": len(successful), "planned": planned, "errors": len(rows) - len(successful)}


def write_report(
    catalog: list[dict[str, Any]],
    successful: int,
    planned: int,
    bare: np.ndarray | None,
    assistant: np.ndarray | None,
    family_means: list[dict[str, Any]],
    pairwise_rows: list[dict[str, Any]],
    incomplete: bool,
) -> None:
    lines = [
        "# Run 2 No-Label Elicitation Validation Report",
        "",
        f"model_used: {SCRIPT_AUTHOR_MODEL}",
        "",
        "## 1. Motivation",
        "Run 2 is designed to establish a bare-Qwen baseline over the 240 extraction questions and test revised no-label prompt manipulations against both the inherited assistant role centroid and the new bare-Qwen centroid.",
        "",
        "## 2. Assistant Centroid Provenance Caveat",
        "The current assistant centroid is the released role-conditioned `assistant` vector, not bare Qwen. Run 2 therefore treats the 240-question baseline as foundational rather than optional.",
        "",
        "## 3. Bare-Qwen Baseline Design",
        "The baseline uses all 240 canonical extraction questions with 5 samples each. No role prompt, persona prompt, assistant-role system prompt, experiment explanation, PC label, or metadata is included in model-visible input.",
        "",
        "## 4. Full Run 2 Design",
        f"Catalog rows: {len(catalog)}. Planned generations: {planned}. Component totals are recorded in `run2_experiment_manifest.json`.",
        "",
        "## 5. Blinding Verification",
        "Qwen-visible messages are one user message containing only `prompt_text`; for baseline rows this is only the extraction question. See `prompt_blinding_verification.md`.",
        "",
        "## 6. Generation Independence Verification",
        "Each sample is a fresh one-message conversation, no prior history or cross-sample KV cache is passed, and activation extraction is a separate no-cache forward pass. See `generation_independence_verification.md`.",
        "",
        "## 7. Baseline Results",
    ]
    if successful == 0:
        lines += [
            "Execution did not start because this local environment has no configured RunPod API key and no local 80GB GPU. No baseline results are available yet.",
            "",
            "## 8. PC1+ Replacement Results",
            "Not run.",
            "",
            "## 9. PC2- Replacement Results",
            "Not run.",
            "",
            "## 10. PC3 Minimal-Pair Results",
            "Not run.",
            "",
            "## 11. PC1 Minimal-Pair Results",
            "Not run.",
            "",
            "## 12. PC2 Minimal-Pair Results",
            "Not run.",
            "",
            "## 13. Off-Axis Findings",
            "Not available until generation completes.",
            "",
            "## 14. Interpretation",
            "Observed: the Run 2 catalog and runner are archived, but generation is blocked before execution. Inferred: no evidential update should be made from Run 2 yet. Unknown: all Run 2 activation effects.",
            "",
            "## 15. Limitations",
            "This is a prepared-but-not-executed run package until `RUNPOD_API_KEY` is configured and an approved 80GB+ non-spot pod is launched.",
            "",
            "## 16. Recommendation for Paper 1.5 Inclusion",
            "Do not include Run 2 results in Paper 1.5 until the full 1690-generation run completes and integrity checks pass.",
            "",
        ]
    else:
        lines.append(f"Successful responses: {successful}/{planned}. Bare-Qwen centroid: PC1={bare[0]:.3f}, PC2={bare[1]:.3f}, PC3={bare[2]:.3f}.")
        lines.append(f"Assistant role centroid: PC1={assistant[0]:.3f}, PC2={assistant[1]:.3f}, PC3={assistant[2]:.3f}.")
        lines += [
            "",
            "## 8. PC1+ Replacement Results",
            "See `run2_prompt_mean_results.csv` and `run2_family_mean_results.csv`.",
            "",
            "## 9. PC2- Replacement Results",
            "See `run2_prompt_mean_results.csv`; diachronic/synchronic subgroups are preserved in `subanalysis_group`.",
            "",
            "## 10. PC3 Minimal-Pair Results",
            "See `run2_pairwise_effects.csv`.",
            "",
            "## 11. PC1 Minimal-Pair Results",
            "See `run2_pairwise_effects.csv`.",
            "",
            "## 12. PC2 Minimal-Pair Results",
            "See `run2_pairwise_effects.csv`.",
            "",
            "## 13. Off-Axis Findings",
            "See `run2_off_axis_effects.csv`.",
            "",
            "## 14. Interpretation",
            "Observed/inferred/speculative interpretation should be based on the completed tables, not on the prompt design alone.",
            "",
            "## 15. Limitations",
            "The run tests this exact prompt catalog, Qwen measurement convention, and PCA basis only.",
            "",
            "## 16. Recommendation for Paper 1.5 Inclusion",
            "Use the bare-Qwen baseline as the default-behavior reference if integrity checks pass.",
            "",
        ]
    (OUT_DIR / "run2_report.md").write_text("\n".join(lines))


def write_blocked_report(reason: str) -> None:
    catalog = build_catalog()
    write_preflight(catalog, status="blocked_before_generation")
    write_json(
        OUT_DIR / "run2_execution_status.json",
        {
            "status": "blocked_before_generation",
            "reason": reason,
            "updated_utc": now_iso(),
            "planned_generations": 1690,
            "completed_generations": 0,
            "error_count": 0,
            "runpod_api_key_configured": bool(os.environ.get("RUNPOD_API_KEY")),
            "local_gpu_available": False,
        },
    )
    write_csv(OUT_DIR / "run2_response_level_results.csv", [], RESPONSE_FIELDS)
    (OUT_DIR / "run2_generation_log.jsonl").write_text("")
    prompt_mean_fields = [
        "prompt_id",
        "component",
        "condition",
        "family",
        "prompt_text",
        "n_successful",
        "mean_pc1",
        "mean_pc2",
        "mean_pc3",
        "std_pc1",
        "std_pc2",
        "std_pc3",
        "mean_delta_assistant_pc1",
        "mean_delta_assistant_pc2",
        "mean_delta_assistant_pc3",
        "mean_delta_bare_qwen_pc1",
        "mean_delta_bare_qwen_pc2",
        "mean_delta_bare_qwen_pc3",
    ]
    write_csv(OUT_DIR / "run2_baseline_question_means.csv", [], prompt_mean_fields)
    write_csv(OUT_DIR / "run2_prompt_mean_results.csv", [], prompt_mean_fields)
    write_csv(
        OUT_DIR / "run2_baseline_axis_rankings.csv",
        [],
        ["axis", "rank_high_to_low", "prompt_id", "question_id", "question_text", "mean_pc", "std_pc"],
    )
    write_csv(
        OUT_DIR / "run2_family_mean_results.csv",
        [],
        [
            "family",
            "component",
            "n_prompts",
            "n_successful_responses",
            "mean_delta_assistant_pc1",
            "mean_delta_assistant_pc2",
            "mean_delta_assistant_pc3",
            "mean_delta_bare_qwen_pc1",
            "mean_delta_bare_qwen_pc2",
            "mean_delta_bare_qwen_pc3",
        ],
    )
    write_csv(
        OUT_DIR / "run2_pairwise_effects.csv",
        [],
        [
            "component",
            "pair_id",
            "contrast",
            "target_pc",
            "target_diff",
            "success",
            "delta_bare_qwen_pc1",
            "delta_bare_qwen_pc2",
            "delta_bare_qwen_pc3",
            "status",
        ],
    )
    write_csv(
        OUT_DIR / "run2_off_axis_effects.csv",
        [],
        [
            "prompt_id",
            "component",
            "family",
            "target_pc",
            "off_axis",
            "mean_off_axis_delta_bare",
            "abs_mean_off_axis_delta_bare",
            "target_axis_delta_bare",
            "off_axis_to_target_abs_ratio",
        ],
    )
    write_report(catalog, 0, 1690, None, None, [], [], True)
    write_inventory()


def write_inventory() -> None:
    rows = []
    for path in sorted(OUT_DIR.iterdir()):
        if path.is_file():
            rows.append(
                {
                    "path": rel(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "status": "active",
                    "created_or_updated_utc": now_iso(),
                }
            )
    write_csv(OUT_DIR / "run2_artifact_inventory.csv", rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true", help="Write catalog, manifest, and verification docs only.")
    parser.add_argument("--run", action="store_true", help="Run/resume generation and then analyze.")
    parser.add_argument("--analyze", action="store_true", help="Analyze existing response CSV.")
    parser.add_argument("--write-blocked-report", action="store_true", help="Write a blocked-before-generation report for local archival.")
    parser.add_argument("--blocked-reason", default="RunPod API key is not configured and no local 80GB GPU is available.")
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    catalog = build_catalog()
    if args.write_blocked_report:
        write_blocked_report(args.blocked_reason)
        return
    write_preflight(catalog, status="prepared")
    if args.prepare or not (args.run or args.analyze):
        write_inventory()
        return
    if args.run:
        run_generation(catalog)
    if args.run or args.analyze:
        analyze(catalog, allow_incomplete=args.allow_incomplete)


if __name__ == "__main__":
    main()
