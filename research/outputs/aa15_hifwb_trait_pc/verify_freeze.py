#!/usr/bin/env python3
"""Verify the AA-15 pre-extraction freeze without constructing vectors."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AA14 = HERE.parent / "three_model_trait_pca"
EXPECTED = "dcac8f8d2e82c6fa337a8c34472b8b1901d7c709823618dd4bf614ed885a46e0"

source = ROOT / "research/outputs/sapa_hifwb_reproducibility/wellbeing_item_freeze.csv"
assert hashlib.sha256(source.read_bytes()).hexdigest() == EXPECTED
frozen = [r for r in csv.DictReader(source.open()) if r["tier"] == "DIRECT"]
items = list(csv.DictReader((HERE / "hifwb_indicator_inventory.csv").open()))
prompts = list(csv.DictReader((HERE / "hifwb_prompt_freeze.csv").open()))
questions = list(csv.DictReader((HERE / "hifwb_extraction_questions.csv").open()))
assert len(frozen) == len(items) == 13
assert [r["item_id"] for r in frozen] == [r["item_id"] for r in items]
assert sum(r["orientation"] == "-" for r in frozen) == 6
assert all(int(r["reverse_keyed"]) == (r["response_direction"] == "-") for r in items)
assert all(a["text"] == b["exact_item_wording"] and a["content"] == b["hifwb_domain"]
           for a, b in zip(frozen, items))
assert len(prompts) == 195
assert {r["formulation"] for r in prompts} == {
    "primary_positive_pole", "exact_survey", "minimal_first_person"}
assert all(sum(r["item_id"] == item and r["formulation"] == form for r in prompts) == 5
           for item in [r["item_id"] for r in items]
           for form in ("primary_positive_pole", "exact_survey", "minimal_first_person"))
assert len(questions) == 8 and [int(r["question_id"]) for r in questions] == [0, 3, 10, 24, 31, 36, 37, 51]
assert all(r["positive_system_prompt"] != r["negative_system_prompt"] for r in prompts)
assert all(r["positive_means_wellbeing"] == "1" for r in prompts if r["formulation"] == "primary_positive_pole")
assert all(r["positive_means_wellbeing"] == "0" for r in prompts
           if r["formulation"] != "primary_positive_pole" and r["original_orientation"] == "-")

models = {}
for model, dim in (("qwen", 5120), ("llama", 8192), ("gemma", 4608)):
    data = np.load(AA14 / f"{model}_trait_pca_directions.npz")
    directions, mean = data["directions"], data["mean"]
    assert directions.shape == (239, dim) and mean.shape == (dim,)
    assert np.isfinite(directions).all() and np.isfinite(mean).all()
    gram = directions[:20] @ directions[:20].T
    assert np.max(abs(gram - np.eye(20))) < 0.001
    models[model] = {"frozen_rank": 239, "feature_dim": dim,
                     "first20_orthogonality_max_error": float(np.max(abs(gram - np.eye(20))))}

checks = {"stage": "pre_extraction", "frozen_sha256": EXPECTED, "direct_items": 13,
          "reverse_keyed": 6, "formulations": 3, "prompt_pairs": 195,
          "questions": 8, "planned_responses_per_model": 3120,
          "aa14_frozen_pca_models": models, "new_indicator_vectors_available": False,
          "viewer_extended": False, "public_aa15_deployment_verified": False}
(HERE / "pre_extraction_verification.json").write_text(json.dumps(checks, indent=2) + "\n")
print(json.dumps(checks, indent=2))
