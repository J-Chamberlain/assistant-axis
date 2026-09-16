#!/usr/bin/env python3
"""Add compact AA-15 projections to AA-14 viewer data; never export activations."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
AA14 = HERE.parent / "three_model_trait_pca"
FORMS = ("primary_positive_pole", "exact_survey", "minimal_first_person")


def read(name: str) -> list[dict]:
    with (HERE / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def indexed(name: str, fields: tuple[str, ...]) -> dict[tuple[str, ...], dict]:
    rows = read(name)
    result = {tuple(row[k] for k in fields): row for row in rows}
    assert len(result) == len(rows), f"Duplicate keys in {name}"
    return result


def main() -> None:
    base = json.loads((AA14 / "viewer_data.json").read_text())
    assert set(base["models"]) == {"qwen", "llama", "gemma"}
    items = indexed("hifwb_indicator_inventory.csv", ("item_id",))
    coords = indexed("hifwb_projection_coordinates.csv", ("model", "item_id", "formulation"))
    diagnostics = indexed("hifwb_projection_diagnostics.csv", ("model", "item_id", "formulation"))
    neighborhoods = indexed("hifwb_trait_neighborhoods.csv", ("model", "item_id", "formulation"))
    stability = indexed("hifwb_prompt_stability.csv", ("model", "item_id", "formulation"))
    compact = indexed("hifwb_cluster_compactness.csv", ("model",))
    centroids = indexed("hifwb_centroid_coordinates.csv", ("model",))
    persona_alignment = indexed("hifwb_persona_alignment.csv", ("model", "name"))
    trait_alignment = indexed("hifwb_trait_alignment.csv", ("model", "name"))
    cross = read("hifwb_cross_model_alignment.csv")
    assert len(items) == 13 and len(coords) == len(diagnostics) == len(neighborhoods) == 117
    assert len(stability) == 78 and len(compact) == len(centroids) == 3
    assert len(cross) == 39
    cross_lookup = defaultdict(list)
    for row in cross:
        cross_lookup[(row["left"], row["item_id"])].append((row["right"], float(row["aligned_item_cosine"])))
        cross_lookup[(row["right"], row["item_id"])].append((row["left"], float(row["aligned_item_cosine"])))
    for model, model_data in base["models"].items():
        model_data["indicators_by_form"] = {}
        model_data["centroid"] = {
            "pcs": [round(float(centroids[(model,)][f"trait_pc{i}"]), 5) for i in range(1, 21)],
            "stable": compact[(model,)]["stable_direction_gate"] == "1",
            "compactness_p": compact[(model,)]["matched_compactness_p"],
        }
        for form in FORMS:
            points = []
            for (item_id,), item in items.items():
                key = (model, item_id, form)
                c, d, n = coords[key], diagnostics[key], neighborhoods[key]
                s = stability.get(key)
                points.append({
                    "name": item_id,
                    "wording": item["exact_item_wording"],
                    "shown_wording": item["primary_positive_pole"] if form == FORMS[0] else
                        item["minimal_first_person"] if form == FORMS[2] else item["exact_item_wording"],
                    "domain": item["hifwb_domain"],
                    "reverse_keyed": item["reverse_keyed"] == "1",
                    "pcs": [round(float(c[f"trait_pc{i}"]), 5) for i in range(1, 21)],
                    "captured": round(float(d["captured_fraction_20"]), 5),
                    "residual": round(float(d["residual_norm_20"]), 5),
                    "nearest": n["nearest_traits"].split(";")[:5],
                    "ood": d["ood"] == "1",
                    "bootstrap_pc90": ([[round(float(d[f"pc{i}_bootstrap_q05"]), 3),
                                          round(float(d[f"pc{i}_bootstrap_q95"]), 3)] for i in range(1, 4)]
                                         if form == FORMS[0] else None),
                    "prompt_cosine_to_primary": None if s is None else round(float(s["raw_vector_cosine_to_primary"]), 4),
                    "cross_model": ([{"model": other, "aligned_cosine": round(value, 4)}
                                     for other, value in sorted(cross_lookup[(model, item_id)])]
                                    if form == FORMS[0] else []),
                })
            assert len(points) == 13
            model_data["indicators_by_form"][form] = points
        for kind, lookup in (("personas", persona_alignment), ("traits", trait_alignment)):
            for point in model_data[kind]:
                row = lookup[(model, point["name"])]
                point["wellbeing_distance"] = round(float(row["distance_to_indicator_centroid_20"]), 5)
                point["wellbeing_alignment"] = round(float(row["signed_projection_on_centroid_direction"]), 5)
                point["wellbeing_direction_stable"] = row["centroid_direction_stable"] == "1"
    base["version"] = "aa15-v1-prospective-analogue"
    base["methodology"] = ("Trait PCA was fitted only to AA-14's 240 contrasts per model. "
                           "HiFWB contrasts are prospective analogues projected afterward; "
                           "the historical trait-response selection is not fully recoverable.")
    destination = HERE / "viewer_data.json"
    destination.write_text(json.dumps(base, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(f"Wrote {destination} ({destination.stat().st_size:,} bytes; no raw activations)")


if __name__ == "__main__":
    main()
