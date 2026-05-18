#!/usr/bin/env python3
"""Compare centered assistant-axis rankings across Gemma, Qwen, and Llama."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch


ROOT = Path(__file__).resolve().parents[3]
VECTOR_ROOT = ROOT / "downloads" / "hf_vectors"
OUTPUT_DIR = ROOT / "research" / "cross_model" / "outputs"

MODELS = {
    "gemma": {"folder": "gemma-2-27b", "fixed_layer": 45, "display": "Gemma 2 27B"},
    "qwen": {"folder": "qwen-3-32b", "fixed_layer": 63, "display": "Qwen 3 32B"},
    "llama": {"folder": "llama-3.3-70b", "fixed_layer": None, "display": "Llama 3.3 70B"},
}


def load_axis(model_dir: Path) -> torch.Tensor:
    path = model_dir / "assistant_axis.pt"
    if not path.exists():
        raise FileNotFoundError(f"Missing axis vector: {path}")
    return torch.load(path, map_location="cpu").float()


def load_role_tensor(model_dir: Path, role_names: list[str]) -> torch.Tensor:
    role_dir = model_dir / "role_vectors"
    if not role_dir.exists():
        raise FileNotFoundError(f"Missing role vector directory: {role_dir}")
    tensors = []
    for role in role_names:
        path = role_dir / f"{role}.pt"
        if not path.exists():
            raise FileNotFoundError(f"Missing role vector for {role}: {path}")
        tensors.append(torch.load(path, map_location="cpu").float())
    return torch.stack(tensors, dim=0)


def unit_rows(x: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    return x / x.norm(dim=-1, keepdim=True).clamp_min(eps)


def raw_projection_by_layer(role_tensor: torch.Tensor, axis: torch.Tensor) -> torch.Tensor:
    return torch.einsum("rld,ld->rl", role_tensor, unit_rows(axis))


def centered_scores(role_tensor: torch.Tensor, axis: torch.Tensor, layer: int) -> torch.Tensor:
    layer_roles = role_tensor[:, layer, :]
    centered = layer_roles - layer_roles.mean(dim=0, keepdim=True)
    axis_unit = axis[layer] / axis[layer].norm().clamp_min(1e-12)
    return torch.mv(centered, axis_unit)


def ranking_df(role_names: list[str], scores: torch.Tensor) -> pd.DataFrame:
    df = pd.DataFrame({"role": role_names, "score": scores.cpu().numpy()})
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


def rank_map(ranking: pd.DataFrame) -> dict[str, int]:
    return dict(zip(ranking["role"], ranking["rank"]))


def spearman_from_ranks(a: dict[str, int], b: dict[str, int], roles: list[str]) -> float:
    n = len(roles)
    d2 = sum((a[role] - b[role]) ** 2 for role in roles)
    return 1.0 - (6.0 * d2) / (n * (n * n - 1))


def format_top_bottom(model_name: str, ranking: pd.DataFrame) -> list[str]:
    lines = [model_name, "-" * len(model_name), "Top 20:"]
    for _, row in ranking.head(20).iterrows():
        lines.append(f"{int(row['rank']):>3}. {row['role']:<24} {row['score']:>12.6f}")
    lines.append("")
    lines.append("Bottom 20:")
    for _, row in ranking.tail(20).iterrows():
        lines.append(f"{int(row['rank']):>3}. {row['role']:<24} {row['score']:>12.6f}")
    return lines


def analyze_model(key: str, role_names: list[str]) -> dict[str, object]:
    spec = MODELS[key]
    model_dir = VECTOR_ROOT / spec["folder"]
    if not model_dir.exists():
        raise FileNotFoundError(f"Missing vector folder: {model_dir}")

    axis_original = load_axis(model_dir)
    role_tensor = load_role_tensor(model_dir, role_names)
    proofreader_idx = role_names.index("proofreader")
    poet_idx = role_names.index("poet")

    raw_probe = raw_projection_by_layer(role_tensor[[proofreader_idx, poet_idx]], axis_original)
    probe_layer = int(raw_probe.var(dim=0, unbiased=False).argmax().item())
    proof_raw = float(raw_probe[0, probe_layer].item())
    poet_raw = float(raw_probe[1, probe_layer].item())
    raw_flip = proof_raw < 0 and poet_raw < 0
    axis_raw_oriented = -axis_original if raw_flip else axis_original

    if spec["fixed_layer"] is None:
        projections = raw_projection_by_layer(role_tensor, axis_raw_oriented)
        variances = projections.var(dim=0, unbiased=False)
        layer = int(variances.argmax().item())
        max_variance = float(variances[layer].item())
    else:
        layer = int(spec["fixed_layer"])
        projections = raw_projection_by_layer(role_tensor, axis_raw_oriented)
        variances = projections.var(dim=0, unbiased=False)
        max_variance = float(variances[layer].item())

    scores = centered_scores(role_tensor, axis_raw_oriented, layer)
    proof_centered = float(scores[proofreader_idx].item())
    poet_centered = float(scores[poet_idx].item())
    centered_flip = proof_centered < poet_centered
    if centered_flip:
        axis_final = -axis_raw_oriented
        scores = -scores
        proof_centered = -proof_centered
        poet_centered = -poet_centered
    else:
        axis_final = axis_raw_oriented

    ranking = ranking_df(role_names, scores)
    return {
        "key": key,
        "display": spec["display"],
        "folder": spec["folder"],
        "axis": axis_final,
        "role_tensor": role_tensor,
        "layer": layer,
        "probe_layer": probe_layer,
        "max_variance": max_variance,
        "raw_flip": raw_flip,
        "centered_flip": centered_flip,
        "proof_raw": proof_raw,
        "poet_raw": poet_raw,
        "proof_centered": proof_centered,
        "poet_centered": poet_centered,
        "ranking": ranking,
        "rank_map": rank_map(ranking),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    role_sets = {}
    for key, spec in MODELS.items():
        role_dir = VECTOR_ROOT / spec["folder"] / "role_vectors"
        if not role_dir.exists():
            raise FileNotFoundError(f"Missing role vectors for {key}: {role_dir}")
        role_sets[key] = set(p.stem for p in role_dir.glob("*.pt"))

    shared_roles = sorted(set.intersection(*role_sets.values()))
    if len(shared_roles) != 275:
        print(f"WARNING: expected 275 shared roles, found {len(shared_roles)}")

    print(f"Loading {len(shared_roles)} shared roles across Gemma, Qwen, and Llama")
    results = {key: analyze_model(key, shared_roles) for key in MODELS}

    comparison = pd.DataFrame({"rank": range(1, len(shared_roles) + 1)})
    for key in MODELS:
        ranking = results[key]["ranking"]
        comparison[f"{key}_role"] = ranking["role"]
        comparison[f"{key}_score"] = ranking["score"]
    comparison.to_csv(OUTPUT_DIR / "three_model_ranking_comparison.csv", index=False)

    spearman_pairs = {
        "Gemma vs Qwen": spearman_from_ranks(results["gemma"]["rank_map"], results["qwen"]["rank_map"], shared_roles),
        "Gemma vs Llama": spearman_from_ranks(results["gemma"]["rank_map"], results["llama"]["rank_map"], shared_roles),
        "Qwen vs Llama": spearman_from_ranks(results["qwen"]["rank_map"], results["llama"]["rank_map"], shared_roles),
    }

    top20 = {key: set(results[key]["ranking"].head(20)["role"]) for key in MODELS}
    all_top20_union = set.union(*top20.values())
    convergent = sorted(set.intersection(*top20.values()))
    model_specific = {
        key: sorted(top20[key] - set.union(*(top20[other] for other in MODELS if other != key)), key=lambda r: results[key]["rank_map"][r])
        for key in MODELS
    }
    not_all_three = sorted(all_top20_union - set(convergent))

    assistant_ranks = {
        key: results[key]["rank_map"]["assistant"]
        for key in MODELS
    }

    top_bottom_lines = ["Three-Model Assistant-Axis Ranking Comparison", "=" * 55, ""]
    for key in MODELS:
        result = results[key]
        top_bottom_lines.extend(
            [
                f"{result['display']} ({result['folder']})",
                f"Layer: {result['layer']}",
                f"Raw sign flip needed: {result['raw_flip']}",
                f"Centered orientation flip needed: {result['centered_flip']}",
                f"Raw sign probe layer: {result['probe_layer']}",
                f"Raw probe scores: proofreader={result['proof_raw']:.6f}, poet={result['poet_raw']:.6f}",
                f"Centered anchor scores: proofreader={result['proof_centered']:.6f}, poet={result['poet_centered']:.6f}",
                f"Layer projection variance: {result['max_variance']:.6f}",
                f"Assistant rank: {assistant_ranks[key]}",
                "",
            ]
        )
        top_bottom_lines.extend(format_top_bottom(result["display"], result["ranking"]))
        top_bottom_lines.append("")
    top_bottom_lines.append("Side-by-side top 20")
    top_bottom_lines.append("rank | gemma_role | qwen_role | llama_role")
    top_bottom_lines.append("-" * 70)
    for i in range(20):
        top_bottom_lines.append(
            f"{i + 1:>4} | "
            f"{results['gemma']['ranking'].iloc[i]['role']:<24} | "
            f"{results['qwen']['ranking'].iloc[i]['role']:<24} | "
            f"{results['llama']['ranking'].iloc[i]['role']:<24}"
        )
    (OUTPUT_DIR / "three_model_top20_bottom20.txt").write_text("\n".join(top_bottom_lines) + "\n")

    convergent_lines = ["Convergent and Model-Specific Top-20 Roles", "=" * 48, ""]
    convergent_lines.append("Roles appearing in all three top-20 lists:")
    for role in convergent:
        convergent_lines.append(
            f"- {role}: Gemma {results['gemma']['rank_map'][role]}, "
            f"Qwen {results['qwen']['rank_map'][role]}, Llama {results['llama']['rank_map'][role]}"
        )
    convergent_lines.append("")
    convergent_lines.append("Roles appearing in at least one top-20 list but not all three:")
    for role in not_all_three:
        present = [key for key in MODELS if role in top20[key]]
        convergent_lines.append(
            f"- {role}: present in {', '.join(present)}; "
            f"Gemma {results['gemma']['rank_map'][role]}, "
            f"Qwen {results['qwen']['rank_map'][role]}, Llama {results['llama']['rank_map'][role]}"
        )
    convergent_lines.append("")
    convergent_lines.append("Model-specific top-20 outliers:")
    for key, roles in model_specific.items():
        convergent_lines.append(f"{results[key]['display']}:")
        if roles:
            for role in roles:
                convergent_lines.append(f"- {role}: rank {results[key]['rank_map'][role]}")
        else:
            convergent_lines.append("- None")
        convergent_lines.append("")
    (OUTPUT_DIR / "three_model_convergent_roles.txt").write_text("\n".join(convergent_lines) + "\n")

    spearman_lines = ["Three-Model Spearman Summary", "=" * 30, ""]
    for label, value in spearman_pairs.items():
        spearman_lines.append(f"{label}: {value:.6f}")
    spearman_lines.append("")
    spearman_lines.append("Assistant ranks:")
    for key in MODELS:
        spearman_lines.append(f"{results[key]['display']}: {assistant_ranks[key]}")
    spearman_lines.append("")
    spearman_lines.append("Layer choices:")
    for key in MODELS:
        spearman_lines.append(f"{results[key]['display']}: layer {results[key]['layer']}")
    (OUTPUT_DIR / "three_model_spearman_summary.txt").write_text("\n".join(spearman_lines) + "\n")

    print("\n".join(spearman_lines))
    print("")
    print("Top 5 roles:")
    for key in MODELS:
        print(f"{results[key]['display']}: {', '.join(results[key]['ranking'].head(5)['role'])}")
    print("")
    print("Bottom 5 roles:")
    for key in MODELS:
        print(f"{results[key]['display']}: {', '.join(results[key]['ranking'].tail(5)['role'])}")
    print("")
    print("Convergent top-20 roles across all three:")
    print(", ".join(convergent) if convergent else "None")
    print("")
    print("Model-specific top-20 outliers:")
    for key, roles in model_specific.items():
        print(f"{results[key]['display']}: {', '.join(roles) if roles else 'None'}")


if __name__ == "__main__":
    main()
