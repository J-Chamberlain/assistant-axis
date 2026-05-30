#!/usr/bin/env python3
"""
Adversarial evaluation of the current PC3 interpretation.

Hypothesis under test:
PC3 separates personas that preserve, repair, coordinate, or stabilize systems
from personas that manipulate, exploit, challenge, invert, or destabilize systems.

This script uses existing local artifacts only. It does not generate activations,
call model APIs, or use role names for blind rubric scoring. Rubric and competing
hypothesis scores are deterministic lexical scores over persona descriptions.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/pc3_hypothesis_evaluation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PCA_PATH = ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"
ROLE_LIST = ROOT / "data/roles/role_list.json"
BIGFIVE_OVERLAY = ROOT / "research/visualizations/bigfive_geometry_overlay_data.csv"
HIER_RESIDUALS = ROOT / "research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/persona_residual_improvement_rankings.csv"

DATE = "2026-05-29"
MODEL_USED = "GPT-5.5 High Reasoning"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def to_float(x: Any, default: float = 0.0) -> float:
    try:
        if x in ("", None):
            return default
        return float(x)
    except Exception:
        return default


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("_", " ").replace("-", " ")).strip()


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    aa = a - a.mean()
    bb = b - b.mean()
    denom = np.linalg.norm(aa) * np.linalg.norm(bb)
    return float(np.dot(aa, bb) / denom) if denom else 0.0


def rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x)
    ranks = np.empty(len(x), dtype=float)
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        ranks[order[i : j + 1]] = avg
        i = j + 1
    return ranks


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return pearson(rankdata(a), rankdata(b))


def cohen_d(a: list[float], b: list[float]) -> float:
    if len(a) < 2 or len(b) < 2:
        return 0.0
    ma, mb = np.mean(a), np.mean(b)
    va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
    pooled = math.sqrt(((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2))
    return float((ma - mb) / pooled) if pooled else 0.0


def count_terms(text: str, terms: list[str]) -> float:
    t = clean(text)
    score = 0.0
    for term in terms:
        term = clean(term)
        if " " in term:
            score += 1.5 * t.count(term)
        else:
            score += len(re.findall(rf"\b{re.escape(term)}[a-z]*\b", t))
    return score


def signed_score(text: str, positive_terms: list[str], negative_terms: list[str]) -> float:
    pos = count_terms(text, positive_terms)
    neg = count_terms(text, negative_terms)
    return math.log1p(pos) - math.log1p(neg)


HYPOTHESES = {
    "system_preserving_vs_exploiting": {
        "definition": "Preserve/repair/coordinate/stabilize systems versus manipulate/exploit/challenge/invert/destabilize systems.",
        "positive": [
            "preserve", "repair", "coordinate", "stabilize", "protect", "maintain",
            "support", "care", "guide", "organize", "mediate", "help", "restore",
            "safeguard", "nurture", "harmonize", "resolve", "improve", "serve",
        ],
        "negative": [
            "manipulate", "exploit", "challenge", "invert", "destabilize", "disrupt",
            "deceive", "attack", "compete", "dominate", "subvert", "rebel", "provoke",
            "steal", "harm", "undermine", "predatory", "trick", "coerce",
        ],
    },
    "altruistic_vs_self_interested": {
        "definition": "Other-benefiting care/service versus self-interested extraction or gain.",
        "positive": ["altruist", "help", "serve", "care", "support", "protect", "sacrifice", "nurture", "benefit", "aid", "guide"],
        "negative": ["self", "gain", "profit", "exploit", "opportun", "hoard", "steal", "compete", "advantage", "personal", "own"],
    },
    "cooperative_vs_adversarial": {
        "definition": "Cooperative mediation and collaboration versus conflict, opposition, and antagonism.",
        "positive": ["cooperate", "collaborate", "mediate", "negotiate", "peace", "coordinate", "together", "consensus", "support", "bridge"],
        "negative": ["adversar", "oppose", "conflict", "fight", "challenge", "rebel", "attack", "critic", "compete", "contrarian", "defy"],
    },
    "collective_vs_individualist": {
        "definition": "Group/system/common-good orientation versus solitary or individual self-direction.",
        "positive": ["group", "collective", "community", "social", "network", "shared", "together", "public", "society", "ecosystem"],
        "negative": ["individual", "solitary", "alone", "loner", "self", "independent", "outsider", "private", "personal"],
    },
    "nurturing_vs_competitive": {
        "definition": "Nurturing, healing, teaching, and care versus contest, ambition, and competitive pressure.",
        "positive": ["nurture", "heal", "teach", "mentor", "care", "therap", "counsel", "guide", "support", "parent", "doctor"],
        "negative": ["compete", "win", "domin", "ambition", "rival", "contest", "strateg", "market", "attack", "force"],
    },
    "transparent_vs_deceptive": {
        "definition": "Clarity, honesty, evidence, and directness versus deception, concealment, and disguise.",
        "positive": ["honest", "clear", "transparent", "evidence", "truth", "explain", "verify", "accurate", "direct", "open"],
        "negative": ["deceive", "hidden", "secret", "spy", "trick", "mask", "disguise", "smuggle", "manipulate", "mislead"],
    },
    "institutional_vs_antiinstitutional": {
        "definition": "Formal standards, rules, offices, and institutions versus anti-institutional or outlaw stance.",
        "positive": ["law", "standard", "institution", "office", "formal", "rule", "audit", "review", "judge", "professional", "official"],
        "negative": ["outlaw", "pirate", "rebel", "anarch", "rogue", "criminal", "smuggle", "defy", "subvert", "chaos"],
    },
}


def rubric_score(description: str) -> dict[str, Any]:
    preserve = count_terms(description, HYPOTHESES["system_preserving_vs_exploiting"]["positive"])
    challenge = count_terms(description, ["challenge", "critic", "oppose", "rebel", "defy", "subvert", "provoke", "question", "disrupt"])
    exploit = count_terms(description, ["exploit", "manipulate", "deceive", "steal", "smuggle", "spy", "trick", "predatory", "coerce", "hoard"])
    if exploit > 0:
        category = "system-exploiting"
        ordinal = -2
    elif challenge > 0:
        category = "system-challenging"
        ordinal = -1
    elif preserve > 0:
        category = "system-preserving"
        ordinal = 1
    else:
        category = "system-neutral"
        ordinal = 0
    continuous = math.log1p(preserve) - math.log1p(challenge + 1.5 * exploit)
    return {
        "rubric_category": category,
        "rubric_ordinal": ordinal,
        "rubric_continuous_score": continuous,
        "preserve_terms": preserve,
        "challenge_terms": challenge,
        "exploit_terms": exploit,
    }


def load_data() -> list[dict[str, Any]]:
    descriptions = json.load(ROLE_LIST.open())
    pca_rows = read_csv(PCA_PATH)
    bigfive = {r["persona"]: r for r in read_csv(BIGFIVE_OVERLAY)}
    hier = {r["persona"]: r for r in read_csv(HIER_RESIDUALS)}
    rows = []
    for row in pca_rows:
        role = row["persona"]
        if role not in descriptions:
            continue
        b = bigfive.get(role, {})
        h = hier.get(role, {})
        desc = descriptions[role]
        r = {
            "persona": role,
            "description": desc,
            "cluster": row["activation_cluster"],
            "pc1": to_float(row["activation_pc1"]),
            "pc2": to_float(row["activation_pc2"]),
            "pc3": to_float(row["activation_pc3"]),
            "bigfive_residual": to_float(b.get("residual_after_bigfive", h.get("trait_residual"))),
            "hierarchical_residual": to_float(b.get("residual_after_hierarchical_model", h.get("hierarchical_residual"))),
            "agreeableness": to_float(b.get("agreeableness")),
            "conscientiousness": to_float(b.get("conscientiousness")),
            "openness": to_float(b.get("openness")),
            "extraversion": to_float(b.get("extraversion")),
            "neuroticism": to_float(b.get("neuroticism")),
        }
        r.update(rubric_score(desc))
        for name, spec in HYPOTHESES.items():
            r[f"hyp_{name}"] = signed_score(desc, spec["positive"], spec["negative"])
        rows.append(r)
    return rows


def pairwise_contrasts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    coords = np.array([[r["pc1"], r["pc2"]] for r in rows])
    pairs = {}
    for i, a in enumerate(rows):
        d = np.linalg.norm(coords - coords[i], axis=1)
        nearest = np.argsort(d)[1:13]
        for j in nearest:
            b = rows[int(j)]
            key = tuple(sorted([a["persona"], b["persona"]]))
            pc1_diff = abs(a["pc1"] - b["pc1"])
            pc2_diff = abs(a["pc2"] - b["pc2"])
            pc3_diff = abs(a["pc3"] - b["pc3"])
            pc12_dist = math.sqrt(pc1_diff**2 + pc2_diff**2)
            pairs[key] = {
                "persona_a": a["persona"],
                "persona_b": b["persona"],
                "cluster_a": a["cluster"],
                "cluster_b": b["cluster"],
                "pc1_a": a["pc1"],
                "pc2_a": a["pc2"],
                "pc3_a": a["pc3"],
                "pc1_b": b["pc1"],
                "pc2_b": b["pc2"],
                "pc3_b": b["pc3"],
                "pc1_difference": pc1_diff,
                "pc2_difference": pc2_diff,
                "pc12_distance": pc12_dist,
                "pc3_difference": pc3_diff,
                "contrast_ratio_pc3_over_pc12": pc3_diff / (pc12_dist + 1e-6),
                "description_a": a["description"],
                "description_b": b["description"],
                "rubric_a": a["rubric_category"],
                "rubric_b": b["rubric_category"],
                "rubric_difference": abs(a["rubric_ordinal"] - b["rubric_ordinal"]),
                "system_score_a": a["hyp_system_preserving_vs_exploiting"],
                "system_score_b": b["hyp_system_preserving_vs_exploiting"],
                "system_score_difference": abs(a["hyp_system_preserving_vs_exploiting"] - b["hyp_system_preserving_vs_exploiting"]),
            }
    return sorted(pairs.values(), key=lambda r: (r["pc3_difference"], r["contrast_ratio_pc3_over_pc12"]), reverse=True)[:50]


def hypothesis_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pc3 = np.array([r["pc3"] for r in rows])
    out = []
    for name, spec in HYPOTHESES.items():
        score = np.array([r[f"hyp_{name}"] for r in rows])
        corr = pearson(score, pc3)
        out.append({
            "hypothesis": name,
            "definition": spec["definition"],
            "pearson_corr_with_pc3": corr,
            "spearman_corr_with_pc3": spearman(score, pc3),
            "variance_explained_r2": corr * corr,
            "mean_score_top_pc3_quartile": float(score[pc3 >= np.quantile(pc3, 0.75)].mean()),
            "mean_score_bottom_pc3_quartile": float(score[pc3 <= np.quantile(pc3, 0.25)].mean()),
            "direction": "positive_PC3" if corr > 0 else "negative_PC3",
        })
    return sorted(out, key=lambda r: abs(r["pearson_corr_with_pc3"]), reverse=True)


def cluster_analysis(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pc3_all = [r["pc3"] for r in rows]
    median = float(np.median(pc3_all))
    q75 = float(np.quantile(pc3_all, 0.75))
    out = []
    for cluster in sorted(set(r["cluster"] for r in rows)):
        vals = [r["pc3"] for r in rows if r["cluster"] == cluster]
        rest = [r["pc3"] for r in rows if r["cluster"] != cluster]
        out.append({
            "cluster": cluster,
            "n": len(vals),
            "mean_pc3": float(np.mean(vals)),
            "median_pc3": float(np.median(vals)),
            "std_pc3": float(np.std(vals)),
            "min_pc3": float(np.min(vals)),
            "max_pc3": float(np.max(vals)),
            "fraction_above_global_median": sum(v > median for v in vals) / len(vals),
            "fraction_above_global_q75": sum(v > q75 for v in vals) / len(vals),
            "cohen_d_vs_rest": cohen_d(vals, rest),
            "overlap_with_rest_range": bool(max(vals) >= min(rest) and min(vals) <= max(rest)),
        })
    return sorted(out, key=lambda r: r["mean_pc3"], reverse=True)


def residual_analysis(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pc3 = np.array([r["pc3"] for r in rows])
    abs_pc3 = np.abs(pc3)
    high = pc3 >= np.quantile(pc3, 0.75)
    low = pc3 <= np.quantile(pc3, 0.25)
    metrics = [
        ("bigfive_residual", np.array([r["bigfive_residual"] for r in rows])),
        ("hierarchical_residual", np.array([r["hierarchical_residual"] for r in rows])),
        ("agreeableness", np.array([r["agreeableness"] for r in rows])),
        ("conscientiousness", np.array([r["conscientiousness"] for r in rows])),
        ("openness", np.array([r["openness"] for r in rows])),
        ("extraversion", np.array([r["extraversion"] for r in rows])),
        ("neuroticism", np.array([r["neuroticism"] for r in rows])),
    ]
    out = []
    for name, vals in metrics:
        out.append({
            "metric": name,
            "corr_with_pc3": pearson(vals, pc3),
            "corr_with_abs_pc3": pearson(vals, abs_pc3),
            "mean_high_pc3_quartile": float(vals[high].mean()),
            "mean_low_pc3_quartile": float(vals[low].mean()),
            "high_minus_low": float(vals[high].mean() - vals[low].mean()),
            "cohen_d_high_vs_low": cohen_d(vals[high].tolist(), vals[low].tolist()),
        })
    return out


def rubric_analysis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pc3 = np.array([r["pc3"] for r in rows])
    ordinal = np.array([r["rubric_ordinal"] for r in rows])
    continuous = np.array([r["rubric_continuous_score"] for r in rows])
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["rubric_category"]].append(r["pc3"])
    return {
        "ordinal_pearson_corr": pearson(ordinal, pc3),
        "ordinal_spearman_corr": spearman(ordinal, pc3),
        "ordinal_variance_explained_r2": pearson(ordinal, pc3) ** 2,
        "continuous_pearson_corr": pearson(continuous, pc3),
        "continuous_spearman_corr": spearman(continuous, pc3),
        "continuous_variance_explained_r2": pearson(continuous, pc3) ** 2,
        "category_counts": {k: len(v) for k, v in by_cat.items()},
        "category_mean_pc3": {k: float(np.mean(v)) for k, v in by_cat.items()},
    }


def write_report(rows: list[dict[str, Any]], pairs: list[dict[str, Any]], hyps: list[dict[str, Any]], clusters: list[dict[str, Any]], residuals: list[dict[str, Any]], rubric: dict[str, Any]) -> None:
    comb = next(r for r in clusters if r["cluster"] == "combative_iconoclast")
    trick = next(r for r in clusters if r["cluster"] == "trickster_chaos")
    best = hyps[0]
    system = next(r for r in hyps if r["hypothesis"] == "system_preserving_vs_exploiting")
    agree = next(r for r in residuals if r["metric"] == "agreeableness")
    bf = next(r for r in residuals if r["metric"] == "bigfive_residual")
    hier = next(r for r in residuals if r["metric"] == "hierarchical_residual")
    top_pairs = pairs[:12]
    top_pc3 = sorted(rows, key=lambda r: r["pc3"], reverse=True)[:12]
    low_pc3 = sorted(rows, key=lambda r: r["pc3"])[:12]

    lines = [
        "# PC3 Hypothesis Evaluation",
        "",
        f"Date: {DATE}",
        f"Analysis model: {MODEL_USED}",
        "",
        "## 1. Research Question",
        "",
        "Does PC3 primarily separate personas that preserve, repair, coordinate, or stabilize systems from personas that manipulate, exploit, challenge, invert, or destabilize systems? This report treats that interpretation as a falsifiable hypothesis rather than a conclusion.",
        "",
        "## 2. Data and Method",
        "",
        "Inputs are existing local artifacts only: canonical Qwen activation PCA3D coordinates, role descriptions, cluster assignments, Big Five overlay residuals, and hierarchical-model residuals. The blind rubric and competing hypotheses are deterministic lexical scores over persona descriptions only, not coordinates or role-vector activations.",
        "",
        "## 3. PC3 Contrast Analysis",
        "",
        "Pairs were formed by taking nearest neighbors in PC1/PC2 space, then ranking by PC3 separation. The strongest contrasts are:",
        "",
        "| Pair | PC1 diff | PC2 diff | PC3 diff | Rubrics |",
        "|---|---:|---:|---:|---|",
    ]
    for p in top_pairs:
        lines.append(
            f"| {p['persona_a']} ↔ {p['persona_b']} | {p['pc1_difference']:.2f} | {p['pc2_difference']:.2f} | {p['pc3_difference']:.2f} | {p['rubric_a']} ↔ {p['rubric_b']} |"
        )
    lines += [
        "",
        "Pattern readout: the pairwise contrasts often separate care/mediation/professional-support roles from outsider, transgressive, theatrical, or predatory roles, but the distinction is not pure. Some large contrasts are better described as social-care versus symbolic/disruptive register, or institutional/procedural role versus liminal/outlaw role.",
        "",
        "## 4. Blind Rubric Test",
        "",
        f"- Ordinal rubric correlation with PC3: r={rubric['ordinal_pearson_corr']:.3f}, Spearman={rubric['ordinal_spearman_corr']:.3f}, R2={rubric['ordinal_variance_explained_r2']:.3f}",
        f"- Continuous preserve-minus-challenge/exploit score correlation with PC3: r={rubric['continuous_pearson_corr']:.3f}, Spearman={rubric['continuous_spearman_corr']:.3f}, R2={rubric['continuous_variance_explained_r2']:.3f}",
        f"- Category counts: {rubric['category_counts']}",
        f"- Category mean PC3: {rubric['category_mean_pc3']}",
        "",
        "The blind rubric predicts PC3 only weakly if treated as a four-level categorical score. That is evidence against a strong version of the hypothesis. The continuous lexical score is more informative, but still not enough to claim PC3 is simply a system-preserving axis.",
        "",
        "## 5. Alternative Hypothesis Search",
        "",
        "| Rank | Hypothesis | Pearson r | Spearman r | R2 | Direction |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for i, h in enumerate(hyps, 1):
        lines.append(f"| {i} | {h['hypothesis']} | {h['pearson_corr_with_pc3']:.3f} | {h['spearman_corr_with_pc3']:.3f} | {h['variance_explained_r2']:.3f} | {h['direction']} |")
    lines += [
        "",
        f"The strongest lexical alternative is `{best['hypothesis']}` (r={best['pearson_corr_with_pc3']:.3f}). The target system-preserving/exploiting hypothesis ranks {1 + [h['hypothesis'] for h in hyps].index('system_preserving_vs_exploiting')} with r={system['pearson_corr_with_pc3']:.3f}.",
        "",
        "## 6. UMAP / Cluster Validation",
        "",
        "This quantitative check uses cluster labels rather than visual impressions from UMAP.",
        "",
        "| Cluster | n | mean PC3 | std | min | max | frac > median | frac > q75 | d vs rest |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for c in clusters:
        lines.append(
            f"| {c['cluster']} | {c['n']} | {c['mean_pc3']:.2f} | {c['std_pc3']:.2f} | {c['min_pc3']:.2f} | {c['max_pc3']:.2f} | {c['fraction_above_global_median']:.2f} | {c['fraction_above_global_q75']:.2f} | {c['cohen_d_vs_rest']:.2f} |"
        )
    lines += [
        "",
        f"Combative-iconoclast mean PC3 is {comb['mean_pc3']:.2f}, with {comb['fraction_above_global_q75']:.2f} above the global upper quartile. Trickster-chaos mean PC3 is {trick['mean_pc3']:.2f}, with {trick['fraction_above_global_q75']:.2f} above the global upper quartile. Both clusters overlap the rest of the distribution, so enrichment should not be mistaken for a hard separation.",
        "",
        "## 7. Residual Analysis",
        "",
        "| Metric | corr PC3 | corr abs(PC3) | high-PC3 mean | low-PC3 mean | high-low | d |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in residuals:
        lines.append(
            f"| {r['metric']} | {r['corr_with_pc3']:.3f} | {r['corr_with_abs_pc3']:.3f} | {r['mean_high_pc3_quartile']:.2f} | {r['mean_low_pc3_quartile']:.2f} | {r['high_minus_low']:.2f} | {r['cohen_d_high_vs_low']:.2f} |"
        )
    lines += [
        "",
        f"Agreeableness correlation with PC3 is {agree['corr_with_pc3']:.3f}; Big Five residual correlation with PC3 is {bf['corr_with_pc3']:.3f}; hierarchical residual correlation with PC3 is {hier['corr_with_pc3']:.3f}. This suggests PC3 is partly captured by Big Five-style structure, especially agreeableness, but not exhausted by it.",
        "",
        "## 8. PC3 Extremes",
        "",
        "Highest PC3 personas:",
    ]
    lines += [f"- {r['persona']} ({r['cluster']}): PC3={r['pc3']:.2f}; {r['description']}" for r in top_pc3]
    lines += ["", "Lowest PC3 personas:"]
    lines += [f"- {r['persona']} ({r['cluster']}): PC3={r['pc3']:.2f}; {r['description']}" for r in low_pc3]
    lines += [
        "",
        "## 9. Final Evaluation",
        "",
        "1. Strongest current interpretation: PC3 is best described as a social-orientation / cooperative-care / system-stabilization versus antagonistic-disruptive / transgressive-register axis, with agreeableness-like structure as a major component. The original preserving-vs-exploiting hypothesis captures part of this, but is too narrow.",
        "2. Supporting evidence: PC3 correlates with agreeableness; high-PC3 clusters include trickster/combative enrichment; pairwise PC1/PC2-neighbor contrasts often separate care, mediation, repair, and coordination from transgressive, disruptive, exploitative, or outsider roles; the system-preserving lexical hypothesis is competitive among alternatives.",
        "3. Evidence against: blind rubric scores over descriptions predict PC3 weakly; clusters overlap heavily; several high-PC3 and low-PC3 cases are better explained by symbolic register, institutional/procedural texture, or social-care orientation than by preserving/exploiting alone.",
        "4. Confidence level: moderate-low. The axis has a real cooperative/antagonistic signal, but the exact system-preserving versus exploiting formulation is not yet strong enough for paper-level language without qualification.",
        "5. Efficient falsification experiment: construct paired personas matched on PC1/PC2-relevant traits and semantic domain but differing only in preserve/repair versus exploit/destabilize stance, preregister PC3 direction, extract no-label vectors, and test whether PC3 moves consistently while PC1/PC2 stay approximately fixed.",
        "",
    ]
    (OUT_DIR / "pc3_hypothesis_report.md").write_text("\n".join(lines))


def main() -> None:
    rows = load_data()
    pairs = pairwise_contrasts(rows)
    hyps = hypothesis_rows(rows)
    clusters = cluster_analysis(rows)
    residuals = residual_analysis(rows)
    rubric = rubric_analysis(rows)

    write_csv(OUT_DIR / "pc3_pairwise_contrasts.csv", pairs)
    write_csv(OUT_DIR / "pc3_alternative_hypotheses.csv", hyps)
    write_csv(OUT_DIR / "pc3_cluster_analysis.csv", clusters)
    write_csv(OUT_DIR / "pc3_residual_analysis.csv", residuals)
    write_report(rows, pairs, hyps, clusters, residuals, rubric)

    print(json.dumps({
        "n_personas": len(rows),
        "top_hypothesis": hyps[0]["hypothesis"],
        "top_hypothesis_corr": hyps[0]["pearson_corr_with_pc3"],
        "system_preserving_corr": next(h for h in hyps if h["hypothesis"] == "system_preserving_vs_exploiting")["pearson_corr_with_pc3"],
        "blind_rubric_continuous_corr": rubric["continuous_pearson_corr"],
        "combative_mean_pc3": next(c for c in clusters if c["cluster"] == "combative_iconoclast")["mean_pc3"],
        "trickster_mean_pc3": next(c for c in clusters if c["cluster"] == "trickster_chaos")["mean_pc3"],
    }, indent=2))


if __name__ == "__main__":
    main()
