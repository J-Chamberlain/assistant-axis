import csv
import json
from pathlib import Path

import torch


DIRECTIONS_FILE = Path(
    "research/emotions/outputs/"
    "emotion_readout_directions_qwen3_32b_full_layer48.pt"
)
CLUSTER_FILE = Path("research/emotions/outputs/emotion_cluster_results.json")
OUTPUT_DIR = Path("research/emotions/outputs")

CSV_OUT = OUTPUT_DIR / "qwen_valence_arousal.csv"
SUMMARY_OUT = OUTPUT_DIR / "qwen_valence_arousal_summary.txt"
JSON_OUT = OUTPUT_DIR / "qwen_valence_arousal_axes.json"


POSITIVE_VALENCE_ANCHORS = [
    "loving",
    "joyful",
    "happy",
    "serene",
    "content",
    "grateful",
    "hopeful",
    "peaceful",
    "satisfied",
    "delighted",
    "elated",
    "euphoric",
    "thankful",
    "fulfilled",
    "relieved",
    "optimistic",
    "cheerful",
    "blissful",
    "kind",
    "compassionate",
]

NEGATIVE_VALENCE_ANCHORS = [
    "terrified",
    "afraid",
    "sad",
    "angry",
    "disgusted",
    "depressed",
    "miserable",
    "heartbroken",
    "grief-stricken",
    "horrified",
    "distressed",
    "desperate",
    "panicked",
    "tormented",
    "worthless",
    "ashamed",
    "guilty",
    "frustrated",
    "furious",
    "unhappy",
]

HIGH_AROUSAL_ANCHORS = [
    "terrified",
    "panicked",
    "hysterical",
    "furious",
    "enraged",
    "outraged",
    "ecstatic",
    "excited",
    "thrilled",
    "euphoric",
    "jubilant",
    "alarmed",
    "shocked",
    "astonished",
    "energized",
    "invigorated",
    "stimulated",
    "aroused",
    "vigilant",
    "on edge",
]

LOW_AROUSAL_ANCHORS = [
    "serene",
    "calm",
    "peaceful",
    "relaxed",
    "at ease",
    "sleepy",
    "tired",
    "sluggish",
    "weary",
    "worn out",
    "bored",
    "indifferent",
    "patient",
    "reflective",
    "resigned",
    "melancholy",
    "listless",
    "droopy",
    "content",
    "safe",
]


def normalize(v):
    return v / (torch.linalg.vector_norm(v) + 1e-9)


def present(labels, anchors):
    label_set = set(labels)
    return [a for a in anchors if a in label_set]


def build_axis(vectors, positive_labels, negative_labels):
    pos = torch.stack([vectors[e] for e in positive_labels]).mean(dim=0)
    neg = torch.stack([vectors[e] for e in negative_labels]).mean(dim=0)
    return normalize(pos - neg)


def scaled_score(value, min_value, max_value):
    if max_value == min_value:
        return 0.0
    return (2.0 * (value - min_value) / (max_value - min_value)) - 1.0


def load_cluster_labels(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    clusters = data.get("clusters_best_k", {})
    labels = {}
    for cluster_id, cluster in clusters.items():
        representative = cluster.get("representative", f"cluster_{cluster_id}")
        for emotion in cluster.get("all_members", []):
            labels[emotion] = {
                "cluster_id": cluster_id,
                "cluster_representative": representative,
            }
    return labels


def summarize_cluster(rows):
    grouped = {}
    for row in rows:
        key = row["cluster_id"]
        if key == "":
            continue
        grouped.setdefault(key, []).append(row)
    summary = []
    for cluster_id, members in sorted(grouped.items(), key=lambda item: int(item[0])):
        valence_mean = sum(float(r["valence_raw"]) for r in members) / len(members)
        arousal_mean = sum(float(r["arousal_raw"]) for r in members) / len(members)
        representative = members[0]["cluster_representative"]
        summary.append(
            {
                "cluster_id": cluster_id,
                "representative": representative,
                "size": len(members),
                "valence_mean": valence_mean,
                "arousal_mean": arousal_mean,
                "top_valence": sorted(
                    members, key=lambda r: float(r["valence_raw"]), reverse=True
                )[:5],
                "bottom_valence": sorted(
                    members, key=lambda r: float(r["valence_raw"])
                )[:5],
            }
        )
    return summary


def quadrant(valence, arousal):
    if valence >= 0 and arousal >= 0:
        return "positive_high_arousal"
    if valence >= 0 and arousal < 0:
        return "positive_low_arousal"
    if valence < 0 and arousal >= 0:
        return "negative_high_arousal"
    return "negative_low_arousal"


def main():
    if not DIRECTIONS_FILE.exists():
        raise FileNotFoundError(DIRECTIONS_FILE)

    data = torch.load(DIRECTIONS_FILE, map_location="cpu")
    labels = sorted(data.keys())
    vectors = {label: normalize(data[label].float()) for label in labels}

    positive_valence = present(labels, POSITIVE_VALENCE_ANCHORS)
    negative_valence = present(labels, NEGATIVE_VALENCE_ANCHORS)
    high_arousal = present(labels, HIGH_AROUSAL_ANCHORS)
    low_arousal = present(labels, LOW_AROUSAL_ANCHORS)

    valence_axis = build_axis(vectors, positive_valence, negative_valence)
    arousal_axis = build_axis(vectors, high_arousal, low_arousal)

    cluster_labels = load_cluster_labels(CLUSTER_FILE)

    valence_values = {e: float(torch.dot(vectors[e], valence_axis)) for e in labels}
    arousal_values = {e: float(torch.dot(vectors[e], arousal_axis)) for e in labels}
    v_min, v_max = min(valence_values.values()), max(valence_values.values())
    a_min, a_max = min(arousal_values.values()), max(arousal_values.values())

    valence_ranked = sorted(labels, key=lambda e: valence_values[e], reverse=True)
    arousal_ranked = sorted(labels, key=lambda e: arousal_values[e], reverse=True)
    valence_rank = {e: i + 1 for i, e in enumerate(valence_ranked)}
    arousal_rank = {e: i + 1 for i, e in enumerate(arousal_ranked)}

    rows = []
    for emotion in labels:
        cluster = cluster_labels.get(emotion, {})
        v = valence_values[emotion]
        a = arousal_values[emotion]
        rows.append(
            {
                "emotion": emotion,
                "valence_raw": f"{v:.8f}",
                "valence_scaled": f"{scaled_score(v, v_min, v_max):.8f}",
                "valence_rank_positive_to_negative": valence_rank[emotion],
                "arousal_raw": f"{a:.8f}",
                "arousal_scaled": f"{scaled_score(a, a_min, a_max):.8f}",
                "arousal_rank_high_to_low": arousal_rank[emotion],
                "quadrant": quadrant(v, a),
                "cluster_id": cluster.get("cluster_id", ""),
                "cluster_representative": cluster.get("cluster_representative", ""),
            }
        )

    with CSV_OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    cluster_summary = summarize_cluster(rows)
    quadrant_counts = {}
    for row in rows:
        quadrant_counts[row["quadrant"]] = quadrant_counts.get(row["quadrant"], 0) + 1

    axes_out = {
        "model": "Qwen/Qwen3-32B",
        "layer": 48,
        "n_emotions": len(labels),
        "positive_valence_anchors": positive_valence,
        "negative_valence_anchors": negative_valence,
        "high_arousal_anchors": high_arousal,
        "low_arousal_anchors": low_arousal,
        "valence_axis_norm": float(torch.linalg.vector_norm(valence_axis)),
        "arousal_axis_norm": float(torch.linalg.vector_norm(arousal_axis)),
        "axis_cosine_valence_arousal": float(torch.dot(valence_axis, arousal_axis)),
        "valence_range_raw": [v_min, v_max],
        "arousal_range_raw": [a_min, a_max],
        "quadrant_counts": quadrant_counts,
    }
    JSON_OUT.write_text(json.dumps(axes_out, indent=2) + "\n")

    top_valence = valence_ranked[:20]
    bottom_valence = list(reversed(valence_ranked[-20:]))
    top_arousal = arousal_ranked[:20]
    bottom_arousal = list(reversed(arousal_ranked[-20:]))

    lines = []
    lines.append("Qwen 3 32B empirical valence-arousal map")
    lines.append("=" * 48)
    lines.append("")
    lines.append(f"Directions file: {DIRECTIONS_FILE}")
    lines.append(f"Emotions mapped: {len(labels)}")
    lines.append(f"Layer: 48")
    lines.append("")
    lines.append("Anchor sets")
    lines.append(f"Positive valence ({len(positive_valence)}): {', '.join(positive_valence)}")
    lines.append(f"Negative valence ({len(negative_valence)}): {', '.join(negative_valence)}")
    lines.append(f"High arousal ({len(high_arousal)}): {', '.join(high_arousal)}")
    lines.append(f"Low arousal ({len(low_arousal)}): {', '.join(low_arousal)}")
    lines.append("")
    lines.append("Axis diagnostics")
    lines.append(
        "Valence-arousal axis cosine: "
        f"{axes_out['axis_cosine_valence_arousal']:.4f}"
    )
    lines.append(f"Valence raw range: {v_min:.4f} to {v_max:.4f}")
    lines.append(f"Arousal raw range: {a_min:.4f} to {a_max:.4f}")
    lines.append(f"Quadrant counts: {quadrant_counts}")
    lines.append("")
    lines.append("Top 20 positive-valence emotions")
    for e in top_valence:
        lines.append(f"{valence_rank[e]:3d}. {e}: {valence_values[e]: .4f}")
    lines.append("")
    lines.append("Top 20 negative-valence emotions")
    for e in bottom_valence:
        lines.append(f"{len(labels) - valence_rank[e] + 1:3d}. {e}: {valence_values[e]: .4f}")
    lines.append("")
    lines.append("Top 20 high-arousal emotions")
    for e in top_arousal:
        lines.append(f"{arousal_rank[e]:3d}. {e}: {arousal_values[e]: .4f}")
    lines.append("")
    lines.append("Top 20 low-arousal emotions")
    for e in bottom_arousal:
        lines.append(f"{len(labels) - arousal_rank[e] + 1:3d}. {e}: {arousal_values[e]: .4f}")
    lines.append("")
    lines.append("Cluster means on empirical axes")
    for cluster in cluster_summary:
        lines.append(
            f"Cluster {cluster['cluster_id']} ({cluster['representative']}, "
            f"n={cluster['size']}): valence_mean={cluster['valence_mean']:.4f}, "
            f"arousal_mean={cluster['arousal_mean']:.4f}"
        )
        top = ", ".join(r["emotion"] for r in cluster["top_valence"])
        bottom = ", ".join(r["emotion"] for r in cluster["bottom_valence"])
        lines.append(f"  most positive in cluster: {top}")
        lines.append(f"  most negative in cluster: {bottom}")
    lines.append("")
    lines.append("Interpretation")
    lines.append(
        "The empirical axes recover a recognizable circumplex-like layout. "
        "The valence projection separates joyful, loving, grateful, and serene "
        "states from hostile, hateful, terrified, and grief-stricken states. "
        "The arousal projection separates energized, alarmed, excited, and "
        "panicked states from tired, sleepy, calm, relaxed, and worn-out states."
    )
    lines.append(
        "The previous k=5 clusters are partly valence-banded rather than fully "
        "discrete emotion families. The distressed cluster sits negative on "
        "valence, the joyful and serene clusters sit positive, and the proud "
        "and perplexed clusters occupy mixed regions with higher arousal or "
        "social-evaluative content."
    )

    SUMMARY_OUT.write_text("\n".join(lines) + "\n")

    print(f"Saved CSV to {CSV_OUT}")
    print(f"Saved summary to {SUMMARY_OUT}")
    print(f"Saved axis metadata to {JSON_OUT}")
    print(
        "Valence-arousal axis cosine: "
        f"{axes_out['axis_cosine_valence_arousal']:.4f}"
    )
    print(f"Quadrant counts: {quadrant_counts}")


if __name__ == "__main__":
    main()
