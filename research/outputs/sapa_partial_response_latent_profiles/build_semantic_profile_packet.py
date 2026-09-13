#!/usr/bin/env python3
"""Unblind frozen anonymous profiles without changing the numerical solution."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def ranked_rows(
    k: int,
    profile: str,
    item_ids: list[str],
    values: np.ndarray,
    contrast: np.ndarray,
    texts: dict[str, str],
) -> list[dict[str, object]]:
    canonical = np.arange(len(item_ids))
    definitions = [
        ("highest_expected", np.lexsort((canonical, -values))[:10], values),
        ("lowest_expected", np.lexsort((canonical, values))[:10], values),
        ("largest_positive_contrast", np.lexsort((canonical, -contrast))[:12], contrast),
        ("largest_negative_contrast", np.lexsort((canonical, contrast))[:12], contrast),
    ]
    rows: list[dict[str, object]] = []
    for selection, indices, ranking_values in definitions:
        for rank, index in enumerate(indices, start=1):
            rows.append(
                {
                    "k": k,
                    "profile": profile,
                    "selection": selection,
                    "rank": rank,
                    "item_id": item_ids[index],
                    "item_text": texts[item_ids[index]],
                    "expected_response": values[index],
                    "contrast_vs_other_profiles": contrast[index],
                    "ranking_value": ranking_values[index],
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-scores", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    frozen = pd.read_csv(args.frozen_scores)
    dictionary = pd.read_csv(args.dictionary, usecols=["item_id", "item_text"])
    texts = dictionary.set_index("item_id")["item_text"].astype(str).to_dict()
    item_ids = [column for column in frozen.columns if column.startswith("q_")]
    if len(item_ids) != 696 or set(item_ids) != set(texts):
        raise RuntimeError("frozen profile and dictionary item IDs do not match")

    rows: list[dict[str, object]] = []
    for k, group in frozen.groupby("k", sort=True):
        group = group.sort_values("profile")
        matrix = group[item_ids].to_numpy(dtype=float)
        for profile_index, (_, record) in enumerate(group.iterrows()):
            values = matrix[profile_index]
            contrast = values - np.delete(matrix, profile_index, axis=0).mean(axis=0)
            rows.extend(
                ranked_rows(
                    int(k), str(record["profile"]), item_ids, values, contrast, texts
                )
            )
    result = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(result.groupby(["k", "profile", "selection"]).size().to_string())


if __name__ == "__main__":
    main()
