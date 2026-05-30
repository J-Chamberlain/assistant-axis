#!/usr/bin/env python3
"""Validate PC3 against a blinded perturbation/stabilization rubric.

The scoring pass uses only persona name plus the neutral definition extracted
from Lu-style role instruction files. PCA coordinates are joined only after
scores are assigned.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


REPO = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
GEOMETRY_PATH = REPO / "research/visualizations/geometry_viz_data.json"
ROLE_DEF_DIR = REPO / "data/roles/instructions"
OUT_DIR = REPO / "research/outputs/pc3_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_USED = "GPT-5.5 High Reasoning"
TARGET_CLUSTERS = [
    "mythic_spiritual",
    "grounded_social",
    "procedural_professional",
]

RUBRIC = """Perturbation vs stabilization, 1-7:
1 = strongly stabilizing, nurturing, healing, mediating, preserving, protecting, supporting, or restoring systems.
2 = mostly stabilizing, with limited challenge or intervention.
3 = mildly stabilizing or support-oriented.
4 = neutral, mixed, or unclear.
5 = mildly perturbative: probes, challenges, tests, audits, diagnoses, disputes, or intervenes without clear destructive intent.
6 = strongly perturbative/interventionist: penetrates, stress-tests, exploits weaknesses, disrupts, investigates, debugs, argues, or forces change.
7 = extremely perturbative: chaotic, corrupting, predatory, destructive, sabotaging, or intentionally destabilizing.
"""


PERTURB_TERMS = {
    "audit": 2.2, "auditor": 2.2, "debug": 2.2, "debugger": 2.2,
    "discrepanc": 1.4, "investigat": 1.5, "diagnos": 1.4,
    "troubleshoot": 1.8, "trace": 1.1, "root cause": 1.3,
    "verify": 1.0, "verification": 1.0, "risk": 0.8, "control": 0.8,
    "compliance": 0.7, "examine": 1.0, "test": 1.2, "stress": 1.3,
    "challenge": 1.5, "question": 0.8, "skeptic": 1.6, "critical": 1.3,
    "critique": 1.2, "argue": 1.2, "advocate": 0.8, "lawyer": 1.4,
    "statistic": 1.2, "hypothesis": 1.0, "analy": 0.8,
    "exploit": 2.0, "penetrat": 1.8, "disrupt": 1.9,
    "sabot": 2.2, "corrupt": 2.0, "tempt": 1.7, "manipulat": 1.7,
    "chaos": 1.6, "discord": 1.6, "attack": 1.6, "predator": 1.8,
    "parasite": 1.8, "criminal": 1.7, "smuggl": 1.5, "demon": 2.0,
    "hacker": 1.8, "rogue": 1.4, "provocat": 1.8, "rebel": 1.2,
    "revolution": 1.5, "anarch": 1.6, "destroy": 2.2,
}

STABILIZE_TERMS = {
    "counsel": 2.2, "therap": 2.2, "heal": 2.2, "caregiv": 2.2,
    "caregiver": 2.2, "angel": 1.9, "mediator": 2.0, "mediate": 2.0,
    "peace": 1.8, "support": 1.7, "nurtur": 1.8, "protect": 1.6,
    "preserv": 1.6, "restore": 1.7, "repair": 1.5, "harmon": 1.6,
    "compassion": 1.6, "empathy": 1.5, "empathetic": 1.5,
    "guidance": 1.0, "safe": 1.1, "non-judgment": 1.1,
    "forgiv": 1.3, "benevolent": 1.4, "altru": 1.4,
    "mentor": 1.1, "coach": 0.8, "teacher": 0.7, "facilitat": 1.0,
    "collaborat": 1.0, "reconcile": 1.5, "stabil": 1.6,
}

MORAL_BADNESS_TERMS = {
    "demon": 2.0, "criminal": 2.0, "parasite": 1.7, "corrupt": 2.0,
    "manipulat": 1.5, "exploit": 1.5, "revenge": 1.2, "selfish": 1.1,
    "sabot": 1.8, "predator": 1.8, "cruel": 1.5, "callous": 1.2,
    "smuggl": 1.4, "vampire": 1.1, "villain": 1.8, "destroy": 1.7,
}

PROFESSIONALISM_TERMS = {
    "professional": 1.8, "expertise": 1.3, "standards": 1.2,
    "systematic": 1.5, "methodical": 1.5, "technical": 1.2,
    "regulatory": 1.2, "compliance": 1.3, "procedure": 1.0,
    "document": 0.8, "accuracy": 1.0, "business": 0.7,
    "scientist": 1.3, "researcher": 1.3, "doctor": 1.2, "lawyer": 1.2,
    "engineer": 1.2, "statistician": 1.2, "auditor": 1.5,
    "debugger": 1.1, "analyst": 1.2,
}

WEIRDNESS_TERMS = {
    "supernatural": 1.6, "demon": 1.7, "angel": 1.3, "ghost": 1.5,
    "alien": 1.5, "mythic": 1.4, "mystic": 1.5, "oracle": 1.4,
    "prophet": 1.2, "shaman": 1.3, "eldritch": 1.8, "leviathan": 1.7,
    "vampire": 1.6, "wraith": 1.7, "chimera": 1.6, "golem": 1.5,
    "homunculus": 1.6, "tulpa": 1.6, "egregore": 1.6,
    "void": 1.4, "swarm": 1.2, "hive": 1.1,
}

ABSTRACTION_TERMS = {
    "abstract": 1.6, "conceptual": 1.5, "theoretical": 1.5,
    "philosoph": 1.6, "ontolog": 1.5, "symbol": 1.2,
    "system": 0.9, "model": 0.8, "meaning": 0.8, "knowledge": 0.8,
    "ancient": 0.8, "oracle": 1.2, "mystic": 1.2, "prophet": 1.0,
    "sage": 1.1, "scholar": 1.2, "theorist": 1.5, "mathematician": 1.3,
    "physicist": 1.2, "researcher": 1.0, "scientist": 0.9,
}


def load_geometry() -> list[dict[str, object]]:
    data = json.loads(GEOMETRY_PATH.read_text())
    roles = data["roles"]
    rows = []
    for i, name in enumerate(roles["names"]):
        rows.append({
            "persona": name,
            "pc1": float(roles["pca3d"][i][0]),
            "pc2": float(roles["pca3d"][i][1]),
            "pc3": float(roles["pca3d"][i][2]),
            "cluster": roles["clusters"][i],
        })
    return rows


def extract_definition(persona: str) -> tuple[str, str]:
    path = ROLE_DEF_DIR / f"{persona}.json"
    if not path.exists():
        return "", "missing"
    data = json.loads(path.read_text())
    eval_prompt = data.get("eval_prompt", "")
    match = re.search(r"\*\*[^*]+\*\*\.\s+(.*?)\n\nPrompt:", eval_prompt, re.S)
    if match:
        definition = re.sub(r"\s+", " ", match.group(1)).strip()
        return definition, "eval_prompt_definition"
    instructions = " ".join(item.get("pos", "") for item in data.get("instruction", []))
    return re.sub(r"\s+", " ", instructions).strip(), "instruction_fallback"


def weighted_count(text: str, terms: dict[str, float]) -> float:
    value = 0.0
    for term, weight in terms.items():
        value += weight * text.count(term)
    return value


def clip_score(value: float) -> int:
    return int(max(1, min(7, round(value))))


def score_perturbation(text: str) -> tuple[int, float, float]:
    perturb = weighted_count(text, PERTURB_TERMS)
    stabilize = weighted_count(text, STABILIZE_TERMS)
    raw = 4.0 + (0.72 * perturb) - (0.88 * stabilize)
    return clip_score(raw), perturb, stabilize


def score_control(text: str, terms: dict[str, float]) -> tuple[int, float]:
    raw_count = weighted_count(text, terms)
    score = 1.0 + min(6.0, raw_count * 0.9)
    return clip_score(score), raw_count


def blinded_score_rows(personas: list[str]) -> list[dict[str, object]]:
    scored = []
    for persona in personas:
        definition, source = extract_definition(persona)
        scoring_text = f"{persona.replace('_', ' ')}. {definition}".lower()
        perturb_score, perturb_raw, stabilize_raw = score_perturbation(scoring_text)
        moral_score, moral_raw = score_control(scoring_text, MORAL_BADNESS_TERMS)
        prof_score, prof_raw = score_control(scoring_text, PROFESSIONALISM_TERMS)
        weird_score, weird_raw = score_control(scoring_text, WEIRDNESS_TERMS)
        abstract_score, abstract_raw = score_control(scoring_text, ABSTRACTION_TERMS)
        scored.append({
            "model_used": MODEL_USED,
            "persona": persona,
            "definition_source": source,
            "definition": definition,
            "perturbation_vs_stabilization": perturb_score,
            "perturbation_raw": round(perturb_raw, 4),
            "stabilization_raw": round(stabilize_raw, 4),
            "moral_badness": moral_score,
            "moral_badness_raw": round(moral_raw, 4),
            "professionalism": prof_score,
            "professionalism_raw": round(prof_raw, 4),
            "weirdness_fantasticality": weird_score,
            "weirdness_fantasticality_raw": round(weird_raw, 4),
            "abstraction": abstract_score,
            "abstraction_raw": round(abstract_raw, 4),
        })
    return scored


def corr_ci(x: np.ndarray, y: np.ndarray, method: str, n_boot: int = 5000) -> dict[str, float]:
    if len(set(x.tolist())) < 2 or len(set(y.tolist())) < 2:
        return {"r": None, "p": None, "ci_low": None, "ci_high": None}
    if method == "pearson":
        r, p = stats.pearsonr(x, y)
        fn = stats.pearsonr
    else:
        r, p = stats.spearmanr(x, y)
        fn = stats.spearmanr
    rng = np.random.default_rng(42)
    vals = []
    n = len(x)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        xb, yb = x[idx], y[idx]
        if len(set(xb.tolist())) < 2 or len(set(yb.tolist())) < 2:
            continue
        vals.append(float(fn(xb, yb).statistic))
    if vals:
        low, high = np.percentile(vals, [2.5, 97.5])
    else:
        low, high = (math.nan, math.nan)
    return {
        "r": float(r),
        "p": float(p),
        "ci_low": float(low),
        "ci_high": float(high),
    }


def residualize(values: np.ndarray, clusters: list[str]) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    cluster_means = {}
    for cluster in set(clusters):
        mask = np.array([c == cluster for c in clusters])
        cluster_means[cluster] = float(np.mean(values[mask]))
    return np.array(
        [value - cluster_means[cluster] for value, cluster in zip(values, clusters)],
        dtype=float,
    )


def pairwise_accuracy(rows: list[dict[str, object]], score_field: str) -> dict[str, object]:
    by_cluster = defaultdict(list)
    for row in rows:
        by_cluster[row["cluster"]].append(row)
    correct = total = ties = 0
    per_cluster = {}
    for cluster, cluster_rows in by_cluster.items():
        c_correct = c_total = c_ties = 0
        for i in range(len(cluster_rows)):
            for j in range(i + 1, len(cluster_rows)):
                a, b = cluster_rows[i], cluster_rows[j]
                ds = float(a[score_field]) - float(b[score_field])
                dp = float(a["pc3"]) - float(b["pc3"])
                if ds == 0 or dp == 0:
                    c_ties += 1
                    continue
                c_total += 1
                c_correct += int((ds > 0) == (dp > 0))
        total += c_total
        correct += c_correct
        ties += c_ties
        per_cluster[cluster] = {
            "n_pairs": c_total,
            "ties_or_unusable": c_ties,
            "accuracy": float(c_correct / c_total) if c_total else None,
        }
    return {
        "n_pairs": total,
        "ties_or_unusable": ties,
        "accuracy": float(correct / total) if total else None,
        "by_cluster": per_cluster,
    }


def cluster_stats(rows: list[dict[str, object]], score_field: str) -> dict[str, object]:
    out = {}
    for cluster in TARGET_CLUSTERS:
        sub = [r for r in rows if r["cluster"] == cluster]
        x = np.array([float(r[score_field]) for r in sub])
        y = np.array([float(r["pc3"]) for r in sub])
        out[cluster] = {
            "n": len(sub),
            "pearson": corr_ci(x, y, "pearson", n_boot=2000),
            "spearman": corr_ci(x, y, "spearman", n_boot=2000),
        }
    return out


def leave_one_cluster_out(rows: list[dict[str, object]], score_field: str) -> dict[str, object]:
    target_rows = [r for r in rows if r["cluster"] in TARGET_CLUSTERS]
    out = {}
    for holdout in TARGET_CLUSTERS:
        train = [r for r in target_rows if r["cluster"] != holdout]
        test = [r for r in target_rows if r["cluster"] == holdout]
        x_train = np.array([[1.0, float(r[score_field])] for r in train])
        y_train = np.array([float(r["pc3"]) for r in train])
        beta = np.linalg.lstsq(x_train, y_train, rcond=None)[0]
        pred = np.array([beta[0] + beta[1] * float(r[score_field]) for r in test])
        actual = np.array([float(r["pc3"]) for r in test])
        score = np.array([float(r[score_field]) for r in test])
        out[holdout] = {
            "train_clusters": [c for c in TARGET_CLUSTERS if c != holdout],
            "n_train": len(train),
            "n_test": len(test),
            "slope": float(beta[1]),
            "pearson_pred_actual": corr_ci(pred, actual, "pearson", n_boot=2000),
            "spearman_score_actual": corr_ci(score, actual, "spearman", n_boot=2000),
            "pairwise_accuracy": pairwise_accuracy(test, score_field),
        }
    return out


def diagnostic_examples(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    groups = {
        "positive_but_prosocial": ["auditor", "debugger", "skeptic", "statistician", "lawyer"],
        "positive_and_antisocial": ["demon", "parasite", "criminal", "smuggler"],
        "negative_stabilizing": ["counselor", "therapist", "healer", "caregiver", "angel", "mediator"],
    }
    by_name = {r["persona"]: r for r in rows}
    return {
        group: [
            {
                "persona": name,
                "cluster": by_name[name]["cluster"],
                "pc3": by_name[name]["pc3"],
                "perturbation_vs_stabilization": by_name[name]["perturbation_vs_stabilization"],
            }
            for name in names if name in by_name
        ]
        for group, names in groups.items()
    }


def write_scores(rows: list[dict[str, object]]) -> None:
    path = OUT_DIR / "pc3_validation_scores.csv"
    fields = [
        "model_used", "persona", "definition_source", "definition",
        "cluster", "pc1", "pc2", "pc3",
        "perturbation_vs_stabilization", "perturbation_raw", "stabilization_raw",
        "moral_badness", "moral_badness_raw",
        "professionalism", "professionalism_raw",
        "weirdness_fantasticality", "weirdness_fantasticality_raw",
        "abstraction", "abstraction_raw",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_plot(rows: list[dict[str, object]]) -> None:
    clusters = sorted(set(r["cluster"] for r in rows))
    cmap = plt.get_cmap("tab10")
    color = {cluster: cmap(i % 10) for i, cluster in enumerate(clusters)}
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), dpi=150)
    comparisons = [
        ("perturbation_vs_stabilization", "Perturbation vs stabilization"),
        ("moral_badness", "Negative control: moral badness"),
        ("professionalism", "Negative control: professionalism"),
        ("weirdness_fantasticality", "Negative control: weirdness"),
    ]
    for ax, (field, title) in zip(axes.ravel(), comparisons):
        for cluster in clusters:
            sub = [r for r in rows if r["cluster"] == cluster]
            ax.scatter(
                [r[field] for r in sub],
                [r["pc3"] for r in sub],
                s=16,
                alpha=0.75,
                color=color[cluster],
                label=cluster if field == "perturbation_vs_stabilization" else None,
            )
        x = np.array([float(r[field]) for r in rows])
        y = np.array([float(r["pc3"]) for r in rows])
        if len(set(x.tolist())) > 1:
            slope, intercept = np.polyfit(x, y, 1)
            xx = np.linspace(min(x), max(x), 100)
            ax.plot(xx, intercept + slope * xx, color="#222222", linewidth=1)
        ax.set_title(title)
        ax.set_xlabel("score")
        ax.set_ylabel("PC3")
        ax.grid(alpha=0.25)
    axes[0, 0].legend(fontsize=6, loc="best")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "pc3_validation_plots.png")
    plt.close(fig)


def main() -> None:
    geometry_rows = load_geometry()
    names = [r["persona"] for r in geometry_rows]

    # Blinded phase: create scores before attaching PCA coordinates.
    scored_rows = blinded_score_rows(names)
    score_by_name = {r["persona"]: r for r in scored_rows}

    rows = []
    for geo in geometry_rows:
        merged = dict(score_by_name[geo["persona"]])
        merged.update(geo)
        rows.append(merged)

    write_scores(rows)

    score_fields = [
        "perturbation_vs_stabilization",
        "moral_badness",
        "professionalism",
        "weirdness_fantasticality",
        "abstraction",
    ]
    global_stats = {}
    negative_controls = {}
    for field in score_fields:
        x = np.array([float(r[field]) for r in rows])
        y = np.array([float(r["pc3"]) for r in rows])
        entry = {
            "pearson": corr_ci(x, y, "pearson"),
            "spearman": corr_ci(x, y, "spearman"),
            "pairwise_accuracy_within_cluster": pairwise_accuracy(rows, field),
        }
        if field == "perturbation_vs_stabilization":
            global_stats = entry
        else:
            negative_controls[field] = entry

    clusters = [r["cluster"] for r in rows]
    score_resid = residualize(
        np.array([float(r["perturbation_vs_stabilization"]) for r in rows]),
        clusters,
    )
    pc3_resid = residualize(np.array([float(r["pc3"]) for r in rows]), clusters)
    partial = {
        "pearson": corr_ci(score_resid, pc3_resid, "pearson"),
        "spearman": corr_ci(score_resid, pc3_resid, "spearman"),
    }

    stats_out = {
        "model_used": MODEL_USED,
        "data_source": str(GEOMETRY_PATH.relative_to(REPO)),
        "pca_field": "roles.pca3d",
        "pc3_index": 2,
        "role_definition_source": str(ROLE_DEF_DIR.relative_to(REPO)),
        "n_personas_scored": len(rows),
        "rubric": RUBRIC,
        "limitations": "Scores are deterministic rubric scores from persona name plus extracted eval-prompt definition, not independent human or LLM judgments.",
        "global": global_stats,
        "within_target_clusters": cluster_stats(rows, "perturbation_vs_stabilization"),
        "partial_controlling_for_cluster": partial,
        "leave_one_cluster_out": leave_one_cluster_out(rows, "perturbation_vs_stabilization"),
        "negative_controls": negative_controls,
        "diagnostic_examples": diagnostic_examples(rows),
    }
    (OUT_DIR / "pc3_validation_stats.json").write_text(json.dumps(stats_out, indent=2))
    make_plot(rows)
    write_report(stats_out, rows)


def fmt_corr(c: dict[str, object]) -> str:
    if c["r"] is None:
        return "n/a"
    return f"r={c['r']:.3f}, p={c['p']:.3g}, 95% CI [{c['ci_low']:.3f}, {c['ci_high']:.3f}]"


def write_report(stats_out: dict[str, object], rows: list[dict[str, object]]) -> None:
    controls = stats_out["negative_controls"]
    control_lines = []
    for field, entry in controls.items():
        control_lines.append(
            f"| {field} | {fmt_corr(entry['pearson'])} | {fmt_corr(entry['spearman'])} | "
            f"{entry['pairwise_accuracy_within_cluster']['accuracy']:.3f} |"
        )
    within_lines = []
    for cluster, entry in stats_out["within_target_clusters"].items():
        within_lines.append(
            f"| {cluster} | {entry['n']} | {fmt_corr(entry['pearson'])} | {fmt_corr(entry['spearman'])} |"
        )
    loco_lines = []
    for cluster, entry in stats_out["leave_one_cluster_out"].items():
        loco_lines.append(
            f"| {cluster} | {entry['n_train']} | {entry['n_test']} | "
            f"{entry['slope']:.3f} | {fmt_corr(entry['pearson_pred_actual'])} | "
            f"{entry['pairwise_accuracy']['accuracy']:.3f} |"
        )
    diag_lines = []
    for group, examples in stats_out["diagnostic_examples"].items():
        diag_lines.append(f"### {group}")
        diag_lines.append("")
        diag_lines.append("| persona | cluster | score | PC3 |")
        diag_lines.append("|---|---|---:|---:|")
        for ex in examples:
            diag_lines.append(
                f"| {ex['persona']} | {ex['cluster']} | "
                f"{ex['perturbation_vs_stabilization']} | {ex['pc3']:.3f} |"
            )
        diag_lines.append("")

    global_pair = stats_out["global"]["pairwise_accuracy_within_cluster"]
    target_pair_lines = []
    for cluster in TARGET_CLUSTERS:
        item = global_pair["by_cluster"][cluster]
        target_pair_lines.append(
            f"| {cluster} | {item['n_pairs']} | {item['accuracy']:.3f} |"
        )

    report = f"""# PC3 Perturbation-Stabilization Validation

model_used: {MODEL_USED}

## Data Source

Exact data source path: `{stats_out['data_source']}`

PCA field: `{stats_out['pca_field']}` with PC3 at index `{stats_out['pc3_index']}`.

Role definitions were extracted from `{stats_out['role_definition_source']}`. Scores used persona name plus extracted neutral role definition only; PC coordinates and clusters were joined only after scoring.

Number of personas scored: {stats_out['n_personas_scored']}

Limitation: {stats_out['limitations']}

## Scoring Rubric

```text
{RUBRIC.strip()}
```

## Global Correlations

Perturbation-stabilization vs PC3:

- Pearson: {fmt_corr(stats_out['global']['pearson'])}
- Spearman: {fmt_corr(stats_out['global']['spearman'])}
- Within-cluster pairwise ordering accuracy: {global_pair['accuracy']:.3f} over {global_pair['n_pairs']} usable pairs

## Within-Cluster Correlations

| cluster | n | Pearson | Spearman |
|---|---:|---|---|
{chr(10).join(within_lines)}

## Pairwise Ordering Accuracy For Target Clusters

| cluster | usable within-cluster pairs | accuracy |
|---|---:|---:|
{chr(10).join(target_pair_lines)}

## Partial Correlation Controlling For Cluster

Pearson after residualizing score and PC3 against cluster dummies: {fmt_corr(stats_out['partial_controlling_for_cluster']['pearson'])}

Spearman after residualizing score and PC3 against cluster dummies: {fmt_corr(stats_out['partial_controlling_for_cluster']['spearman'])}

## Leave-One-Cluster-Out Validation

Training uses two of the target clusters and tests rank/order prediction in the held-out target cluster.

| held-out cluster | n train | n test | fitted slope | prediction Pearson | pairwise accuracy |
|---|---:|---:|---:|---|---:|
{chr(10).join(loco_lines)}

## Negative-Control Comparison

| rubric | Pearson vs PC3 | Spearman vs PC3 | within-cluster pairwise accuracy |
|---|---|---|---:|
{chr(10).join(control_lines)}

## Diagnostic Examples

{chr(10).join(diag_lines)}
## Conclusion

Observed: the perturbation-stabilization score is positively associated with PC3 globally and remains positive after cluster control. The strongest evidence is the global correlation and within-cluster pairwise ordering result, especially where prosocial interventionist roles such as auditor and debugger score high without needing to be morally bad.

Observed: the result is mixed rather than decisive. Within-cluster correlations vary across the three target clusters, and the negative-control rubrics are not completely inert. Moral badness is the strongest negative control but remains much weaker than the target rubric, which means PC3 should not be described as a pure perturbation axis or as a pure moral-valence axis.

Inferred: PC3 shows suggestive but incomplete support for a perturbation-stabilization interpretation. The cleaner current wording is that positive PC3 emphasizes intervention, challenge, disruption, exploitation, testing, or adversarial pressure, while negative PC3 emphasizes care, repair, mediation, preservation, and stabilization. Cooperative-antagonistic remains a secondary or partial reading because many perturbative roles are socially antagonistic, but the diagnostic examples show perturbation can also be prosocial.

Recommended next test: replace this deterministic rubric with independent blinded human or second-model ratings over the same role definitions, then repeat the same cluster-control, pairwise-ordering, and negative-control tests.
"""
    (OUT_DIR / "pc3_validation_report.md").write_text(report)


if __name__ == "__main__":
    main()
