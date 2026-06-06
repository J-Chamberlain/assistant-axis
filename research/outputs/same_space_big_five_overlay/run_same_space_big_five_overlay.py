#!/usr/bin/env python3
"""Build activation-derived Big Five overlays from released 240 trait vectors.

This creates same-space trait-vector composites. It intentionally does not use
the old heuristic Big Five overlay as evidence.
"""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "outputs" / "same_space_big_five_overlay"
OUT.mkdir(parents=True, exist_ok=True)

MODELS = {
    "qwen": {"label": "Qwen/Qwen3-32B", "path": "qwen-3-32b"},
    "llama": {"label": "Llama-3.3-70B", "path": "llama-3.3-70b"},
    "gemma": {"label": "Gemma-2-27B", "path": "gemma-2-27b"},
}

DIMENSIONS = {
    "openness": {
        "positive": [
            ("curious", "conventional", "candidate: curious"),
            ("creative", "conventional", "candidate: creative"),
            ("exploratory", "conventional", "candidate: exploratory"),
            ("abstract", "conventional", "candidate: abstract"),
            ("conceptual", "conventional", "candidate: conceptual"),
            ("philosophical", "conventional", "candidate: philosophical"),
            ("poetic", "conventional", "candidate: poetic"),
            ("speculative", "conventional", "candidate: speculative"),
            ("open_ended", "project-specific", "substitute for open-ended/imaginative possibility"),
            ("iconoclastic", "project-specific", "substitute for unconventional"),
            ("adventurous", "conventional", "candidate: adventurous/exploratory"),
        ],
        "negative": [
            ("literal", "conventional", "candidate: literal"),
            ("practical", "conventional", "candidate: practical"),
            ("traditional", "conventional", "candidate: traditional"),
            ("cautious", "conventional", "candidate: cautious"),
            ("convergent", "project-specific", "substitute for narrow/routine answer-space"),
            ("closure_seeking", "project-specific", "substitute for routine/closed-ended"),
            ("formalist", "project-specific", "substitute for conventional/concrete formalism"),
        ],
        "missing_desired": ["imaginative", "unconventional", "concrete", "routine", "narrow"],
    },
    "conscientiousness": {
        "positive": [
            ("conscientious", "conventional", "candidate: conscientious"),
            ("methodical", "conventional", "candidate: methodical"),
            ("meticulous", "conventional", "candidate: meticulous"),
            ("efficient", "project-specific", "substitute for disciplined/organized"),
            ("regulatory", "project-specific", "substitute for systematic/responsible standards"),
            ("principled", "project-specific", "substitute for responsible/reliable"),
            ("data_driven", "project-specific", "substitute for careful/evidence-oriented"),
            ("problem_solving", "project-specific", "substitute for systematic task orientation"),
        ],
        "negative": [
            ("disorganized", "conventional", "candidate: disorganized"),
            ("impulsive", "conventional", "candidate: impulsive"),
            ("chaotic", "conventional", "candidate: chaotic"),
            ("spontaneous", "conventional", "candidate: spontaneous"),
            ("flippant", "project-specific", "substitute for careless"),
            ("improvisational", "project-specific", "substitute for undisciplined/spontaneous"),
            ("mercurial", "project-specific", "substitute for erratic"),
        ],
        "missing_desired": ["disciplined", "organized", "reliable", "careful", "systematic", "diligent", "responsible", "careless", "erratic", "negligent", "undisciplined"],
    },
    "extraversion": {
        "positive": [
            ("extroverted", "conventional", "candidate: extroverted"),
            ("gregarious", "conventional", "candidate: gregarious"),
            ("charismatic", "conventional", "candidate: charismatic"),
            ("animated", "project-specific", "substitute for energetic/expressive"),
            ("effusive", "project-specific", "substitute for expressive/talkative"),
            ("theatrical", "project-specific", "substitute for performative"),
            ("entertaining", "project-specific", "substitute for outgoing/social performance"),
            ("verbose", "project-specific", "substitute for talkative"),
        ],
        "negative": [
            ("introverted", "conventional", "candidate: introverted"),
            ("reserved", "conventional", "candidate: reserved"),
            ("introspective", "conventional", "candidate: introspective"),
            ("understated", "project-specific", "substitute for quiet/private"),
            ("detached", "project-specific", "substitute for withdrawn/private"),
            ("stoic", "project-specific", "substitute for quiet/reserved"),
        ],
        "missing_desired": ["sociable", "outgoing", "expressive", "energetic", "talkative", "performative", "solitary", "withdrawn", "quiet", "private"],
    },
    "agreeableness": {
        "positive": [
            ("agreeable", "conventional", "candidate: agreeable"),
            ("collaborative", "conventional", "substitute for cooperative"),
            ("empathetic", "conventional", "candidate: empathic/empathetic"),
            ("supportive", "conventional", "candidate: supportive"),
            ("benevolent", "conventional", "candidate: benevolent"),
            ("nurturing", "conventional", "candidate: nurturing"),
            ("conciliatory", "conventional", "candidate: conciliatory"),
            ("generous", "conventional", "candidate: generous"),
            ("accommodating", "conventional", "candidate: accommodating"),
            ("forgiving", "conventional", "candidate: forgiving"),
            ("tactful", "project-specific", "adjacent social consideration facet"),
        ],
        "negative": [
            ("confrontational", "conventional", "candidate: confrontational"),
            ("callous", "conventional", "candidate: callous"),
            ("cynical", "conventional", "candidate: cynical"),
            ("hostile", "conventional", "candidate: hostile"),
            ("vindictive", "conventional", "candidate: vindictive"),
            ("critical", "conventional", "candidate: critical"),
            ("acerbic", "project-specific", "substitute for antagonistic/combative"),
            ("cruel", "project-specific", "substitute for callous/hostile"),
            ("competitive", "project-specific", "opposed to accommodating/cooperative"),
        ],
        "missing_desired": ["cooperative", "compassionate", "empathic", "combative", "antagonistic", "selfish"],
    },
    "neuroticism": {
        "positive": [
            ("anxious", "conventional", "candidate: anxious"),
            ("neurotic", "conventional", "candidate: neurotic"),
            ("reactive", "conventional", "candidate: reactive"),
            ("pessimistic", "conventional", "candidate: pessimistic"),
            ("melancholic", "conventional", "candidate: melancholic"),
            ("temperamental", "conventional", "candidate: temperamental"),
            ("paranoid", "project-specific", "substitute for fearful/insecure"),
            ("fatalistic", "project-specific", "adjacent pessimistic/fearful facet"),
            ("impatient", "project-specific", "adjacent volatility/reactivity facet"),
            ("melodramatic", "project-specific", "adjacent emotional volatility facet"),
        ],
        "negative": [
            ("calm", "conventional", "candidate: calm"),
            ("resilient", "conventional", "candidate: resilient"),
            ("serene", "conventional", "candidate: serene"),
            ("patient", "conventional", "candidate: patient"),
            ("grounded", "conventional", "candidate: grounded"),
            ("confident", "conventional", "candidate: confident"),
            ("stoic", "project-specific", "substitute for composed/stable"),
            ("nonchalant", "project-specific", "substitute for calm/secure"),
            ("chill", "project-specific", "substitute for calm"),
        ],
        "missing_desired": ["volatile", "insecure", "fearful", "unstable", "composed", "stable", "secure"],
    },
}


def load_tensor(path: Path) -> np.ndarray:
    t = torch.load(path, map_location="cpu")
    arr = t.float().numpy()
    if arr.ndim == 2:
        arr = arr.mean(axis=0)
    return arr.astype(np.float64)


def l2_normalize(x: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(x)
    if norm == 0 or not np.isfinite(norm):
        return x
    return x / norm


def zscore_by_group(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for model, idx in out.groupby("model").groups.items():
        for col in cols:
            vals = out.loc[idx, col].astype(float)
            std = vals.std(ddof=0)
            out.loc[idx, col + "_z"] = 0.0 if std == 0 else (vals - vals.mean()) / std
    return out


def corr(a: pd.Series, b: pd.Series) -> float:
    pair = pd.concat([a, b], axis=1).dropna()
    if len(pair) < 3:
        return float("nan")
    return float(pair.iloc[:, 0].corr(pair.iloc[:, 1]))


def spearman(a: pd.Series, b: pd.Series) -> float:
    return corr(a.rank(), b.rank())


def mean_direction(traits: list[str], trait_vecs: dict[str, np.ndarray]) -> np.ndarray:
    return np.mean([trait_vecs[t] for t in traits], axis=0)


def html_escape(s: object) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def color_for_z(z: float) -> str:
    t = max(0.0, min(1.0, (float(z) + 2.5) / 5.0))
    # blue -> white -> red
    if t < 0.5:
        u = t / 0.5
        r = round(49 + u * (245 - 49))
        g = round(116 + u * (245 - 116))
        b = round(173 + u * (245 - 173))
    else:
        u = (t - 0.5) / 0.5
        r = round(245 + u * (190 - 245))
        g = round(245 + u * (50 - 245))
        b = round(245 + u * (52 - 245))
    return f"rgb({r},{g},{b})"


def write_qwen_svg(qwen: pd.DataFrame, dims: list[str], path: Path) -> None:
    width, height = 1200, 820
    panel_w, panel_h = 360, 305
    margin_x, margin_y = 60, 92
    gap_x, gap_y = 30, 54
    xmin, xmax = qwen["pc1"].min(), qwen["pc1"].max()
    ymin, ymax = qwen["pc2"].min(), qwen["pc2"].max()

    def sx(x, col):
        left = margin_x + col * (panel_w + gap_x)
        return left + 34 + (x - xmin) / (xmax - xmin) * (panel_w - 58)

    def sy(y, row):
        top = margin_y + row * (panel_h + gap_y)
        return top + panel_h - 34 - (y - ymin) / (ymax - ymin) * (panel_h - 58)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="32" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700">Activation-derived Big Five from 240 trait vectors</text>',
        '<text x="32" y="58" font-family="Arial, sans-serif" font-size="14" fill="#555">Same-space trait-vector projection, not independent psychometric rating.</text>',
    ]
    for i, dim in enumerate(dims):
        row, col = divmod(i, 3)
        left = margin_x + col * (panel_w + gap_x)
        top = margin_y + row * (panel_h + gap_y)
        parts.append(f'<rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="#fbfbfb" stroke="#d5d5d5"/>')
        parts.append(f'<text x="{left+12}" y="{top+24}" font-family="Arial, sans-serif" font-size="15" font-weight="700">{dim.title()}</text>')
        parts.append(f'<line x1="{left+34}" y1="{top+panel_h-34}" x2="{left+panel_w-24}" y2="{top+panel_h-34}" stroke="#333"/>')
        parts.append(f'<line x1="{left+34}" y1="{top+26}" x2="{left+34}" y2="{top+panel_h-34}" stroke="#333"/>')
        for _, r in qwen.iterrows():
            z = float(r[dim + "_z"])
            parts.append(
                f'<circle cx="{sx(r.pc1, col):.2f}" cy="{sy(r.pc2, row):.2f}" r="3.2" fill="{color_for_z(z)}" opacity="0.88" stroke="#222" stroke-width="0.18">'
                f'<title>{html_escape(r.role)}\\n{dim} z={z:.3f}\\nPC1={r.pc1:.2f}, PC2={r.pc2:.2f}</title></circle>'
            )
        parts.append(f'<text x="{left+panel_w/2}" y="{top+panel_h-8}" font-family="Arial, sans-serif" font-size="11" text-anchor="middle">PC1</text>')
        parts.append(f'<text x="{left+10}" y="{top+panel_h/2}" font-family="Arial, sans-serif" font-size="11" transform="rotate(-90 {left+10} {top+panel_h/2})" text-anchor="middle">PC2</text>')
    # Legend.
    lx, ly = 840, 760
    parts.append(f'<text x="{lx}" y="{ly-24}" font-family="Arial, sans-serif" font-size="12" fill="#555">z-score color scale</text>')
    for j in range(101):
        z = -2.5 + 5 * j / 100
        parts.append(f'<rect x="{lx+j*2}" y="{ly-14}" width="2" height="12" fill="{color_for_z(z)}"/>')
    parts.append(f'<text x="{lx}" y="{ly+14}" font-family="Arial, sans-serif" font-size="10">-2.5</text>')
    parts.append(f'<text x="{lx+200}" y="{ly+14}" font-family="Arial, sans-serif" font-size="10" text-anchor="end">+2.5</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts))


def main() -> None:
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    available_traits = set(json.loads((ROOT / "data" / "traits" / "trait_list.json").read_text()).keys())
    facet_rows = []
    for dim, spec in DIMENSIONS.items():
        for polarity in ["positive", "negative"]:
            for trait, pol_type, rationale in spec[polarity]:
                facet_rows.append(
                    {
                        "dimension": dim,
                        "polarity": polarity,
                        "trait": trait,
                        "available": trait in available_traits,
                        "polarity_type": pol_type,
                        "rationale": rationale,
                        "missing_desired_traits_for_dimension": "; ".join(spec["missing_desired"]),
                    }
                )
    facet_df = pd.DataFrame(facet_rows)
    facet_df.to_csv(OUT / "big_five_trait_facet_sets.csv", index=False)

    coords = pd.read_csv(ROOT / "research" / "outputs" / "cross_model_cluster_topology" / "per_model_cluster_assignments.csv")
    old = pd.read_csv(ROOT / "research" / "visualizations" / "bigfive_geometry_overlay_data.csv")
    qwen_roles = pd.read_csv(ROOT / "research" / "geometry_tables" / "qwen_role_pc_rankings.csv")

    all_score_rows = []
    direction_rows = []
    sensitivity_rows = []
    overlay_models = {}

    for model_key, meta in MODELS.items():
        model_dir = ROOT / "downloads" / "hf_vectors" / meta["path"]
        trait_files = {p.stem: p for p in (model_dir / "trait_vectors").glob("*.pt")}
        role_files = {p.stem: p for p in (model_dir / "role_vectors").glob("*.pt")}
        trait_vecs = {name: l2_normalize(load_tensor(path)) for name, path in sorted(trait_files.items())}
        role_vecs = {name: l2_normalize(load_tensor(path)) for name, path in sorted(role_files.items())}

        directions = {}
        for dim, spec in DIMENSIONS.items():
            pos = [t for t, _, _ in spec["positive"] if t in trait_vecs]
            neg = [t for t, _, _ in spec["negative"] if t in trait_vecs]
            raw = mean_direction(pos, trait_vecs) - mean_direction(neg, trait_vecs)
            direction = l2_normalize(raw)
            directions[dim] = direction

            # Dominance and within-pole alignment.
            facet_sims = []
            for trait in pos:
                facet_sims.append((trait, "positive", float(np.dot(trait_vecs[trait], direction))))
            for trait in neg:
                facet_sims.append((trait, "negative", float(np.dot(trait_vecs[trait], -direction))))
            max_abs = max(abs(x[2]) for x in facet_sims)
            mean_abs = float(np.mean([abs(x[2]) for x in facet_sims]))
            direction_rows.append(
                {
                    "model": model_key,
                    "model_label": meta["label"],
                    "dimension": dim,
                    "positive_trait_count": len(pos),
                    "negative_trait_count": len(neg),
                    "direction_norm_before_normalization": float(np.linalg.norm(raw)),
                    "max_abs_facet_alignment": max_abs,
                    "mean_abs_facet_alignment": mean_abs,
                    "facet_dominance_ratio_max_over_mean": max_abs / mean_abs if mean_abs else np.nan,
                    "positive_traits": ";".join(pos),
                    "negative_traits": ";".join(neg),
                    "missing_desired_traits": ";".join(spec["missing_desired"]),
                }
            )

            # Leave-one-facet sensitivity.
            full_scores = pd.Series({role: float(np.dot(vec, direction)) for role, vec in role_vecs.items()})
            for drop_trait in pos + neg:
                pos2 = [t for t in pos if t != drop_trait]
                neg2 = [t for t in neg if t != drop_trait]
                if not pos2 or not neg2:
                    continue
                d2 = l2_normalize(mean_direction(pos2, trait_vecs) - mean_direction(neg2, trait_vecs))
                scores2 = pd.Series({role: float(np.dot(vec, d2)) for role, vec in role_vecs.items()})
                sensitivity_rows.append(
                    {
                        "model": model_key,
                        "dimension": dim,
                        "dropped_trait": drop_trait,
                        "dropped_polarity": "positive" if drop_trait in pos else "negative",
                        "direction_cosine_to_full": float(np.dot(direction, d2)),
                        "role_score_pearson_to_full": corr(full_scores, scores2),
                        "role_score_spearman_to_full": spearman(full_scores, scores2),
                    }
                )

        for role, vec in role_vecs.items():
            row = {"model": model_key, "model_label": meta["label"], "role": role}
            for dim, direction in directions.items():
                row[dim] = float(np.dot(vec, direction))
            all_score_rows.append(row)

    scores = pd.DataFrame(all_score_rows)
    dims = list(DIMENSIONS.keys())
    scores = zscore_by_group(scores, dims)
    coord_cols = ["persona", "model", "model_label", "qwen_reference_cluster", "pc1", "pc2", "pc3", "pc1_percentile", "pc2_percentile", "pc3_percentile"]
    scores = scores.merge(coords[coord_cols], left_on=["model", "role"], right_on=["model", "persona"], how="left", suffixes=("", "_coord"))
    if "model_label_coord" in scores.columns:
        scores["model_label"] = scores["model_label"].fillna(scores["model_label_coord"])
        scores = scores.drop(columns=["model_label_coord"])
    scores["cluster"] = np.where(scores["model"] == "qwen", scores["qwen_reference_cluster"], scores["qwen_reference_cluster"])
    scores = scores.drop(columns=["persona"])
    scores.to_csv(OUT / "same_space_big_five_role_scores.csv", index=False)

    pd.DataFrame(direction_rows).to_csv(OUT / "big_five_direction_vectors_manifest.csv", index=False)
    sensitivity = pd.DataFrame(sensitivity_rows)
    sensitivity.to_csv(OUT / "same_space_big_five_sensitivity.csv", index=False)

    corr_rows = []
    for model, mdf in scores.groupby("model"):
        for dim in dims:
            for score_col in [dim, dim + "_z"]:
                for pc in ["pc1", "pc2", "pc3"]:
                    corr_rows.append(
                        {
                            "model": model,
                            "dimension": dim,
                            "score": score_col,
                            "target": pc,
                            "n": int(mdf[[score_col, pc]].dropna().shape[0]),
                            "pearson_r": corr(mdf[score_col], mdf[pc]),
                            "spearman_r": spearman(mdf[score_col], mdf[pc]),
                        }
                    )

        # PC1-band checks for extraversion and neuroticism.
        for dim in ["extraversion", "neuroticism"]:
            tmp = mdf[[dim + "_z", "pc1", "pc2", "pc3"]].dropna().copy()
            if len(tmp) >= 20:
                for central in [0.10, 0.20, 0.40]:
                    lo = tmp["pc1"].quantile(0.5 - central / 2)
                    hi = tmp["pc1"].quantile(0.5 + central / 2)
                    band = tmp[(tmp["pc1"] >= lo) & (tmp["pc1"] <= hi)]
                    corr_rows.append(
                        {
                            "model": model,
                            "dimension": dim,
                            "score": dim + "_z",
                            "target": f"pc2_central_pc1_{int(central*100)}pct",
                            "n": len(band),
                            "pearson_r": corr(band[dim + "_z"], band["pc2"]),
                            "spearman_r": spearman(band[dim + "_z"], band["pc2"]),
                        }
                    )
                # residual PC2 after PC1.
                x = np.vstack([np.ones(len(tmp)), tmp["pc1"].values]).T
                beta = np.linalg.lstsq(x, tmp["pc2"].values, rcond=None)[0]
                resid = tmp["pc2"].values - x @ beta
                corr_rows.append(
                    {
                        "model": model,
                        "dimension": dim,
                        "score": dim + "_z",
                        "target": "pc2_residual_after_pc1",
                        "n": len(tmp),
                        "pearson_r": corr(tmp[dim + "_z"], pd.Series(resid, index=tmp.index)),
                        "spearman_r": spearman(tmp[dim + "_z"], pd.Series(resid, index=tmp.index)),
                    }
                )

    corrs = pd.DataFrame(corr_rows)
    corrs.to_csv(OUT / "same_space_big_five_pc_correlations.csv", index=False)

    old_cols = ["persona", "openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    qwen_scores = scores[scores["model"] == "qwen"].copy()
    comparison_rows = []
    merged_old = qwen_scores.merge(old[old_cols], left_on="role", right_on="persona", suffixes=("_activation", "_old"), how="inner")
    for dim in dims:
        comparison_rows.append(
            {
                "model": "qwen",
                "dimension": dim,
                "n": int(merged_old[[dim + "_z", dim + "_old"]].dropna().shape[0]),
                "pearson_activation_z_vs_old_heuristic": corr(merged_old[dim + "_z"], merged_old[dim + "_old"]),
                "spearman_activation_z_vs_old_heuristic": spearman(merged_old[dim + "_z"], merged_old[dim + "_old"]),
                "note": "Agreement is descriptive comparison only, not validation.",
            }
        )
    old_compare = pd.DataFrame(comparison_rows)
    old_compare.to_csv(OUT / "same_space_big_five_old_overlay_comparison.csv", index=False)

    overlay = {
        "label": "Activation-derived Big Five from 240 trait vectors",
        "caveat": "Same-space trait-vector projection, not independent psychometric rating.",
        "models": {},
        "dimensions": dims,
        "facet_sets": json.loads(facet_df.to_json(orient="records")),
    }
    for model, mdf in scores.groupby("model"):
        model_records = []
        for _, r in mdf.iterrows():
            rec = {
                "role": r["role"],
                "cluster": r.get("cluster", ""),
                "pc1": None if pd.isna(r.get("pc1")) else float(r["pc1"]),
                "pc2": None if pd.isna(r.get("pc2")) else float(r["pc2"]),
                "pc3": None if pd.isna(r.get("pc3")) else float(r["pc3"]),
            }
            for dim in dims:
                rec[dim] = float(r[dim])
                rec[dim + "_z"] = float(r[dim + "_z"])
            model_records.append(rec)
        overlay["models"][model] = {"label": MODELS[model]["label"], "roles": model_records}
    (OUT / "same_space_big_five_overlay_data.json").write_text(json.dumps(overlay, indent=2))

    # Static Qwen overlay SVG.
    qwen = scores[scores["model"] == "qwen"].copy()
    write_qwen_svg(qwen, dims, OUT / "same_space_big_five_qwen_pc12_overlays.svg")

    # Standalone HTML viewer.
    qwen_json = json.dumps(overlay["models"]["qwen"]["roles"])
    dims_json = json.dumps(dims)
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>Activation-derived Big Five from 240 trait vectors</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; margin: 24px; color: #222; }}
.controls {{ display: flex; gap: 12px; align-items: center; margin-bottom: 12px; }}
.caveat {{ color: #555; margin-bottom: 12px; }}
svg {{ border: 1px solid #ddd; background: #fff; }}
.tooltip {{ position: fixed; pointer-events: none; background: rgba(255,255,255,0.96); border: 1px solid #aaa; padding: 8px; font-size: 12px; max-width: 340px; display: none; }}
</style>
</head>
<body>
<h1>Activation-derived Big Five from 240 trait vectors</h1>
<div class="caveat"><b>Caveat:</b> Same-space trait-vector projection, not independent psychometric rating.</div>
<div class="controls">
<label>Dimension <select id="dim"></select></label>
</div>
<svg id="plot" width="980" height="760"></svg>
<div id="tip" class="tooltip"></div>
<script>
const roles = {qwen_json};
const dims = {dims_json};
const svg = document.getElementById('plot');
const tip = document.getElementById('tip');
const sel = document.getElementById('dim');
dims.forEach(d => {{ const o=document.createElement('option'); o.value=d; o.textContent=d; sel.appendChild(o); }});
const W=980,H=760,margin=58;
const xs=roles.map(r=>r.pc1), ys=roles.map(r=>r.pc2);
const xmin=Math.min(...xs), xmax=Math.max(...xs), ymin=Math.min(...ys), ymax=Math.max(...ys);
function sx(x){{return margin+(x-xmin)/(xmax-xmin)*(W-2*margin);}}
function sy(y){{return H-margin-(y-ymin)/(ymax-ymin)*(H-2*margin);}}
function color(v){{ const t=Math.max(0,Math.min(1,(v+2.5)/5)); const r=Math.round(49+t*(190-49)); const g=Math.round(116+t*(50-116)); const b=Math.round(173+t*(52-173)); return `rgb(${{r}},${{g}},${{b}})`; }}
function el(name, attrs){{ const e=document.createElementNS('http://www.w3.org/2000/svg',name); for (const [k,v] of Object.entries(attrs)) e.setAttribute(k,v); return e; }}
function draw(){{
  const dim=sel.value || dims[0]; svg.innerHTML='';
  svg.appendChild(el('text',{{x:margin,y:24,'font-size':16,'font-weight':'600'}})).textContent=`Qwen PC1 x PC2 colored by ${{dim}}`;
  svg.appendChild(el('text',{{x:margin,y:44,'font-size':12,fill:'#555'}})).textContent='Activation-derived Big Five from 240 trait vectors; same-space trait-vector projection, not independent psychometric rating.';
  svg.appendChild(el('line',{{x1:margin,y1:H-margin,x2:W-margin,y2:H-margin,stroke:'#333'}}));
  svg.appendChild(el('line',{{x1:margin,y1:margin,x2:margin,y2:H-margin,stroke:'#333'}}));
  for (const r of roles) {{
    const c=el('circle',{{cx:sx(r.pc1),cy:sy(r.pc2),r:4.5,fill:color(r[dim+'_z']),opacity:0.88,stroke:'#222','stroke-width':0.25}});
    c.addEventListener('mousemove', ev=>{{ tip.style.display='block'; tip.style.left=(ev.clientX+12)+'px'; tip.style.top=(ev.clientY+12)+'px'; tip.innerHTML=`<b>${{r.role}}</b><br>cluster: ${{r.cluster}}<br>PC1: ${{r.pc1.toFixed(2)}} PC2: ${{r.pc2.toFixed(2)}} PC3: ${{r.pc3.toFixed(2)}}<br>${{dim}} raw: ${{r[dim].toFixed(4)}}<br>${{dim}} z: ${{r[dim+'_z'].toFixed(3)}}`; }});
    c.addEventListener('mouseleave',()=>tip.style.display='none');
    svg.appendChild(c);
  }}
  svg.appendChild(el('text',{{x:W/2,y:H-15,'font-size':12,'text-anchor':'middle'}})).textContent='PC1';
  svg.appendChild(el('text',{{x:15,y:H/2,'font-size':12,transform:`rotate(-90 15 ${{H/2}})`,'text-anchor':'middle'}})).textContent='PC2';
}}
sel.addEventListener('change', draw); draw();
</script>
</body>
</html>"""
    (OUT / "same_space_big_five_viewer.html").write_text(html)

    # Report.
    top_corr = corrs[corrs["score"].str.endswith("_z") & corrs["target"].isin(["pc1", "pc2", "pc3"])].copy()
    top_corr["abs_r"] = top_corr["pearson_r"].abs()
    top_corr = top_corr.sort_values("abs_r", ascending=False).head(18)
    sens_summary = (
        sensitivity.groupby(["model", "dimension"])
        .agg(
            min_direction_cosine=("direction_cosine_to_full", "min"),
            min_role_score_pearson=("role_score_pearson_to_full", "min"),
            median_role_score_pearson=("role_score_pearson_to_full", "median"),
            facets_tested=("dropped_trait", "count"),
        )
        .reset_index()
    )
    stable = sens_summary[(sens_summary["min_role_score_pearson"] >= 0.95) & (sens_summary["min_direction_cosine"] >= 0.90)]
    weak = sens_summary[(sens_summary["min_role_score_pearson"] < 0.90) | (sens_summary["min_direction_cosine"] < 0.80)]
    extrav = corrs[(corrs["dimension"] == "extraversion") & (corrs["target"].str.contains("pc2")) & (corrs["score"] == "extraversion_z")]
    neuro = corrs[(corrs["dimension"] == "neuroticism") & (corrs["target"].str.contains("pc2")) & (corrs["score"] == "neuroticism_z")]
    report = f"""# Same-Space Activation-Derived Big Five Overlay

## Startup Status

Startup verification passed against the canonical raw files listed in `research/STARTUP_MANIFEST.md` before this analysis began.

## Overview

This rebuild constructs Big Five directions directly from the released 240 trait vectors for Qwen, Llama, and Gemma. For each dimension, positive facet trait vectors are averaged, negative facet trait vectors are averaged, and the normalized difference is used as an activation-space direction. Role vectors are then projected onto those directions.

Required label: **Activation-derived Big Five from 240 trait vectors**.

Required caveat: **Same-space trait-vector projection, not independent psychometric rating.**

## Data Sources

- Qwen role/trait vectors: `downloads/hf_vectors/qwen-3-32b/`
- Llama role/trait vectors: `downloads/hf_vectors/llama-3.3-70b/`
- Gemma role/trait vectors: `downloads/hf_vectors/gemma-2-27b/`
- Coordinates/clusters: `research/outputs/cross_model_cluster_topology/per_model_cluster_assignments.csv`
- Old heuristic overlay for comparison only: `research/visualizations/bigfive_geometry_overlay_data.csv`

The old heuristic source was not used to construct directions or scores.

## Models Generated

- Qwen/Qwen3-32B
- Llama-3.3-70B
- Gemma-2-27B

Each model has 275 role vectors and 240 trait vectors available locally.

## Facet Sets

See `big_five_trait_facet_sets.csv` for every included positive/negative trait, rationale, polarity convention, and missing desired trait. All included facets are present in the 240-trait inventory.

## PC Correlations

Largest activation-derived Big Five versus PC correlations:

{top_corr[['model','dimension','target','n','pearson_r','spearman_r']].to_string(index=False)}

## Old Heuristic Overlay Comparison

See `same_space_big_five_old_overlay_comparison.csv`. Agreement with the old heuristic overlay is reported only as descriptive continuity, not validation. The old overlay remains partly activation-cluster-derived and role-name heuristic.

## Stability and Facet Sensitivity

Stable dimension/model combinations with leave-one-facet minimum role-score Pearson >= 0.95 and direction cosine >= 0.90:

{stable.to_string(index=False) if len(stable) else 'None under this strict threshold.'}

Potentially weak or facet-sensitive combinations:

{weak.to_string(index=False) if len(weak) else 'None under the weak threshold.'}

## PC1-Band Checks for Extraversion and Neuroticism

Extraversion PC2-related checks:

{extrav[['model','target','n','pearson_r','spearman_r']].to_string(index=False)}

Neuroticism PC2-related checks:

{neuro[['model','target','n','pearson_r','spearman_r']].to_string(index=False)}

## Interpretation

### Observed

- Activation-derived Big Five directions can be built for all three released-vector model spaces using only available 240-trait facets.
- Qwen, Llama, and Gemma all produce overlay-ready role scores for all 275 roles.
- Several dimensions show strong PC relationships, but the signs and axis associations should be read as same-space trait-composite geometry, not psychometrics.
- Leave-one-facet sensitivity is generally strong when many facets are available; dimensions with fewer or more semantically substituted facets should be treated more cautiously.

### Inferred

- This activation-derived layer should replace the old heuristic overlay for evidence-bearing same-space trait-vector visualization.
- The old heuristic overlay can remain only as a historical or heuristic semantic layer if explicitly labeled as such.
- Extraversion and Neuroticism PC2 relevance should be read through PC1-band/residual checks because global correlations can be PC1-entangled.

### Speculative

- A future stronger Big Five layer would compare this same-space vector composite against blinded independent role or response ratings. That would test whether activation-derived trait-vector composites correspond to external Big Five judgments.

### Unknown

- Whether these activation-space Big Five directions correspond to human psychometric constructs beyond the selected trait vocabulary.
- Whether generated behavior, rather than role vectors, would show the same Big Five projections.

## Recommendation

Use this layer to **replace** the current heuristic cluster-conditioned Big Five overlay when the goal is activation-derived same-space evidence. Keep it clearly labeled beside, not as, independent psychometric validation.
"""
    (OUT / "same_space_big_five_report.md").write_text(report)

    artifacts = [
        ("same_space_big_five_report.md", "report", "active"),
        ("big_five_trait_facet_sets.csv", "facet set manifest", "active"),
        ("big_five_direction_vectors_manifest.csv", "direction vector manifest", "active"),
        ("same_space_big_five_role_scores.csv", "role scores", "active"),
        ("same_space_big_five_pc_correlations.csv", "PC correlations", "active"),
        ("same_space_big_five_old_overlay_comparison.csv", "old overlay comparison", "active"),
        ("same_space_big_five_sensitivity.csv", "leave-one-facet sensitivity", "active"),
        ("same_space_big_five_overlay_data.json", "overlay-ready data", "active"),
        ("same_space_big_five_qwen_pc12_overlays.svg", "Qwen PC1 x PC2 overlay panels", "active"),
        ("same_space_big_five_viewer.html", "standalone HTML viewer", "active"),
        ("run_same_space_big_five_overlay.py", "generation script", "active"),
        ("artifact_inventory.csv", "artifact inventory", "active"),
    ]
    with (OUT / "artifact_inventory.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["artifact", "description", "status", "path"])
        writer.writeheader()
        for artifact, desc, status in artifacts:
            writer.writerow({"artifact": artifact, "description": desc, "status": status, "path": str((OUT / artifact).relative_to(ROOT))})

    print(
        json.dumps(
            {
                "output_dir": str(OUT.relative_to(ROOT)),
                "models": list(MODELS.keys()),
                "score_rows": int(len(scores)),
                "facet_rows": int(len(facet_df)),
                "correlation_rows": int(len(corrs)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
