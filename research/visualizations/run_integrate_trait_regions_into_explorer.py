#!/usr/bin/env python3
"""Integrate Qwen PC1 x PC2 trait-region overlays into the persona explorer."""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPLORER = ROOT / "research/visualizations/persona_geometry_explorer.html"
CELLS_CSV = ROOT / "research/outputs/qwen_pc2_trait_region_overlay/qwen_pc1_pc2_trait_region_cells.csv"
JOINED_MATRIX = ROOT / "research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv"
DATA_OUT = ROOT / "research/visualizations/trait_region_overlay_data.json"
REPORT_OUT = ROOT / "research/visualizations/trait_region_overlay_integration_report.md"
PREVIEW_OUT = ROOT / "research/visualizations/trait_region_overlay_preview.png"

META = {
    "persona",
    "pc1",
    "pc2",
    "pc3",
    "cluster",
    "pc1_percentile",
    "pc2_percentile",
    "pc3_percentile",
}
CLUSTER_ORDER = [
    "editorial",
    "procedural_professional",
    "grounded_social",
    "other",
    "combative_iconoclast",
    "mythic_spiritual",
    "trickster_chaos",
    "unassigned",
]


def fnum(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return float("nan")


def parse_trait_scores(text: str) -> list[dict[str, float | str]]:
    out = []
    for part in (text or "").split(";"):
        if ":" not in part:
            continue
        name, score = part.split(":", 1)
        out.append({"trait": name.strip(), "score": fnum(score.strip())})
    return out


def parse_csv_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def quantile_cells() -> list[dict]:
    with CELLS_CSV.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    cells = []
    for row in rows:
        cells.append(
            {
                "basis": "quantile",
                "basis_label": "Quantile bands",
                "cell_id": f"quantile_{row['pc1_bin']}_{row['pc2_bin']}",
                "pc1_band": row["pc1_bin"],
                "pc2_band": row["pc2_bin"],
                "pc1_min": fnum(row["pc1_min"]),
                "pc1_max": fnum(row["pc1_max"]),
                "pc2_min": fnum(row["pc2_min"]),
                "pc2_max": fnum(row["pc2_max"]),
                "role_count": int(row["role_count"]),
                "dominant_cluster": row["dominant_cluster"],
                "dominant_cluster_fraction": fnum(row["dominant_cluster_fraction"]),
                "top_local_trait_names": [x.strip() for x in row["top_band_relative_trait_names"].split(",") if x.strip()],
                "top_local_traits": parse_trait_scores(row["top_band_relative_traits"]),
                "top_global_trait_names": [x.strip() for x in row["top_global_trait_names"].split(",") if x.strip()],
                "top_global_traits": parse_trait_scores(row["top_global_traits"]),
                "example_roles": [x.strip() for x in row["example_roles"].split(",") if x.strip()],
                "sparse_cell": parse_csv_bool(row["sparse_cell"]),
                "method_note": "Existing 5 x 3 PC1-quantile and within-band PC2-tertile analysis; default because cell sizes are stable.",
            }
        )
    return cells


def fixed_grid_cells() -> list[dict]:
    with JOINED_MATRIX.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        row["pc1"] = fnum(row["pc1"])
        row["pc2"] = fnum(row["pc2"])
        for key in row:
            if key not in META:
                row[key] = fnum(row[key])
    trait_cols = [c for c in rows[0] if c not in META]
    pc1_min, pc1_max = min(r["pc1"] for r in rows), max(r["pc1"] for r in rows)
    pc2_min, pc2_max = min(r["pc2"] for r in rows), max(r["pc2"] for r in rows)
    pc1_edges = [pc1_min + (pc1_max - pc1_min) * i / 5 for i in range(6)]
    pc2_edges = [pc2_min + (pc2_max - pc2_min) * i / 3 for i in range(4)]
    global_mean = {t: statistics.fmean(r[t] for r in rows) for t in trait_cols}
    global_std = {}
    for t in trait_cols:
        sd = statistics.pstdev(r[t] for r in rows)
        global_std[t] = sd if sd > 1e-12 else 1.0

    def bin_index(value: float, edges: list[float]) -> int:
        for i in range(len(edges) - 1):
            lo, hi = edges[i], edges[i + 1]
            if i == len(edges) - 2:
                if lo <= value <= hi:
                    return i
            elif lo <= value < hi:
                return i
        return max(0, min(len(edges) - 2, len(edges) - 2))

    for row in rows:
        row["_pc1_bin"] = bin_index(row["pc1"], pc1_edges)
        row["_pc2_bin"] = bin_index(row["pc2"], pc2_edges)

    band_means = {}
    for bi in range(5):
        band = [r for r in rows if r["_pc1_bin"] == bi]
        band_means[bi] = {t: statistics.fmean(r[t] for r in band) for t in trait_cols}

    cells = []
    for bi in range(5):
        for cj in range(3):
            sub = [r for r in rows if r["_pc1_bin"] == bi and r["_pc2_bin"] == cj]
            if not sub:
                continue
            cell_mean = {t: statistics.fmean(r[t] for r in sub) for t in trait_cols}
            local_scores = sorted(
                [(t, (cell_mean[t] - band_means[bi][t]) / global_std[t]) for t in trait_cols],
                key=lambda x: x[1],
                reverse=True,
            )
            global_scores = sorted(
                [(t, (cell_mean[t] - global_mean[t]) / global_std[t]) for t in trait_cols],
                key=lambda x: x[1],
                reverse=True,
            )
            clusters = Counter(r["cluster"] for r in sub)
            dominant, dom_n = clusters.most_common(1)[0]
            xmid = (pc1_edges[bi] + pc1_edges[bi + 1]) / 2
            ymid = (pc2_edges[cj] + pc2_edges[cj + 1]) / 2
            examples = sorted(
                sub,
                key=lambda r: ((r["pc1"] - xmid) ** 2 + (r["pc2"] - ymid) ** 2, r["persona"]),
            )[:8]
            pc2_label = ["low", "mid", "high"][cj]
            cells.append(
                {
                    "basis": "explorer_grid",
                    "basis_label": "Explorer fixed grid",
                    "cell_id": f"explorer_C{bi + 1}_{pc2_label}",
                    "pc1_band": f"C{bi + 1}",
                    "pc2_band": pc2_label,
                    "pc1_min": pc1_edges[bi],
                    "pc1_max": pc1_edges[bi + 1],
                    "pc2_min": pc2_edges[cj],
                    "pc2_max": pc2_edges[cj + 1],
                    "role_count": len(sub),
                    "dominant_cluster": dominant,
                    "dominant_cluster_fraction": dom_n / len(sub),
                    "top_local_trait_names": [t for t, _ in local_scores[:8]],
                    "top_local_traits": [{"trait": t, "score": float(s)} for t, s in local_scores[:8]],
                    "top_global_trait_names": [t for t, _ in global_scores[:8]],
                    "top_global_traits": [{"trait": t, "score": float(s)} for t, s in global_scores[:8]],
                    "example_roles": [r["persona"] for r in examples],
                    "sparse_cell": len(sub) < 8,
                    "method_note": "Equal-width PC1 x PC2 grid in explorer coordinates; descriptive and sparse cells should not be over-interpreted.",
                }
            )
    return cells


def build_overlay_data() -> dict:
    quantile = quantile_cells()
    explorer = fixed_grid_cells()
    return {
        "metadata": {
            "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "model_used": "GPT-5.5",
            "source_quantile_cells": str(CELLS_CSV.relative_to(ROOT)),
            "source_joined_trait_matrix": str(JOINED_MATRIX.relative_to(ROOT)),
            "default_basis": "quantile",
            "default_label_count": 3,
            "sparse_threshold": 8,
            "provenance_note": "Trait-region labels are Qwen activation-space trait-vector cosine enrichments. The trait matrix has mixed provenance and is not an independent psychological rating table.",
        },
        "bases": {
            "quantile": {
                "label": "Quantile bands",
                "description": "Five equal-count PC1 quantile bands crossed with within-band PC2 tertiles. This is the statistically stable default.",
                "cells": quantile,
            },
            "explorer_grid": {
                "label": "Explorer fixed grid",
                "description": "Equal-width PC1 x PC2 cells in explorer coordinates. This aligns with the native scatter geometry but is descriptive and can be sparse.",
                "cells": explorer,
            },
        },
    }


def inject_once(text: str, needle: str, replacement: str, label: str) -> str:
    if replacement in text:
        return text
    if needle not in text:
        raise RuntimeError(f"Could not find insertion point for {label}")
    return text.replace(needle, replacement, 1)


def update_explorer(overlay: dict) -> None:
    html = EXPLORER.read_text()

    css = """
    .trait-region-note {
      display: none;
      padding: 0 18px 14px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.5;
      max-width: 980px;
    }
    .trait-region-note.active { display: block; }
    .region-detail {
      display: none;
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid #202026;
    }
    .region-detail.active { display: block; }
    .region-detail .region-chip {
      display: inline-block;
      border: 1px solid #444;
      border-radius: 999px;
      padding: 3px 7px;
      margin: 0 4px 5px 0;
      font-size: 10px;
      color: #e8e8e8;
      background: #18181e;
    }
    .region-detail .region-text {
      color: var(--muted);
      font-size: 11px;
      line-height: 1.55;
      margin-top: 8px;
    }
"""
    html = inject_once(html, "    @media (max-width: 900px) {", css + "    @media (max-width: 900px) {", "trait-region CSS")

    html = html.replace(
        '<div class="control-group" id="colorControls"><span class="label">Color</span><button id="colorCluster" class="active">Cluster</button><button id="colorAxis">Axis Projection</button><select id="colorBigFive"></select></div>',
        '<div class="control-group" id="colorControls"><span class="label">Color</span><button id="colorCluster" class="active">Cluster</button><button id="colorAxis">Axis Projection</button><button id="colorRegionCluster">Region Cluster</button><select id="colorBigFive"></select></div>\n    <div class="control-group" id="traitRegionControls"><span class="label">Trait regions</span><select id="traitRegionLevel"><option value="0">Off</option><option value="1">Top 1</option><option value="3">Top 3</option><option value="5">Top 5</option></select><span class="label">Region basis</span><select id="traitRegionBasis"><option value="quantile">Quantile bands</option><option value="explorer_grid">Explorer grid</option></select></div>',
    )
    html = inject_once(
        html,
        '<div class="range-note" id="rangeNote"></div>',
        '<div class="range-note" id="rangeNote"></div>\n      <div class="trait-region-note" id="traitRegionNote"></div>',
        "trait-region note",
    )
    html = inject_once(
        html,
        '<div class="hint">Big Five-style LLM-assigned trait features were the strongest global predictor of canonical activation PCA in the shared benchmark, improving held-out PCA3D R² from semantic baseline ≈0.389 to ≈0.613. These overlays allow inspection of how trait scores vary across PCA and UMAP views.</div>',
        '<div class="hint">Big Five-style LLM-assigned trait features were the strongest global predictor of canonical activation PCA in the shared benchmark, improving held-out PCA3D R² from semantic baseline ≈0.389 to ≈0.613. These overlays allow inspection of how trait scores vary across PCA and UMAP views.</div>\n      <div class="region-detail" id="regionDetail"><div class="panel-title">Trait Region</div><div id="regionDetailBody" class="region-text">Hover or click a trait-region label.</div></div>',
        "trait-region side panel",
    )
    html = inject_once(
        html,
        "    const DATASET_KEYS = Object.keys(VIZ_DATA).filter(k => ['roles', 'traits', 'emotions'].includes(k));",
        "    const TRAIT_REGION_OVERLAY = " + json.dumps(overlay, separators=(",", ":")).replace("</", "<\\/") + ";\n    const DATASET_KEYS = Object.keys(VIZ_DATA).filter(k => ['roles', 'traits', 'emotions'].includes(k));",
        "trait-region data",
    )
    html = inject_once(
        html,
        "    let colorMode = 'cluster';\n    let pinned = null;",
        "    let colorMode = 'cluster';\n    let traitRegionLevel = 0;\n    let traitRegionBasis = TRAIT_REGION_OVERLAY.metadata.default_basis || 'quantile';\n    let pinnedRegion = null;\n    let pinned = null;",
        "trait-region globals",
    )
    html = inject_once(
        html,
        "      document.getElementById('colorAxis').onclick = () => { colorMode = 'axis'; updateButtons(); render(); };\n      document.getElementById('colorBigFive').onchange = e => { if (e.target.value) colorMode = e.target.value; updateButtons(); render(); };",
        "      document.getElementById('colorAxis').onclick = () => { colorMode = 'axis'; updateButtons(); render(); };\n      document.getElementById('colorRegionCluster').onclick = () => { colorMode = 'trait_region_cluster'; updateButtons(); render(); };\n      document.getElementById('colorBigFive').onchange = e => { if (e.target.value) colorMode = e.target.value; updateButtons(); render(); };\n      document.getElementById('traitRegionLevel').onchange = e => { traitRegionLevel = Number(e.target.value); if (traitRegionLevel > 0) syncTraitRegionView(); pinnedRegion = null; updateButtons(); render(); };\n      document.getElementById('traitRegionBasis').onchange = e => { traitRegionBasis = e.target.value; if (traitRegionLevel > 0) syncTraitRegionView(); pinnedRegion = null; updateButtons(); render(); };",
        "trait-region control handlers",
    )
    html = inject_once(
        html,
        "      document.getElementById('colorAxis').classList.toggle('active', colorMode === 'axis');\n      const bigFiveSelect = document.getElementById('colorBigFive');",
        "      document.getElementById('colorAxis').classList.toggle('active', colorMode === 'axis');\n      document.getElementById('colorRegionCluster').classList.toggle('active', colorMode === 'trait_region_cluster');\n      document.getElementById('traitRegionLevel').value = String(traitRegionLevel);\n      document.getElementById('traitRegionBasis').value = traitRegionBasis;\n      const bigFiveSelect = document.getElementById('colorBigFive');",
        "trait-region button state",
    )
    html = inject_once(
        html,
        "    function isBigFiveColorMode(mode) {\n      return mode === 'dominant_bigfive_trait' || mode === 'residual_after_bigfive' || mode.startsWith('big5_');\n    }\n",
        """    function isBigFiveColorMode(mode) {
      return mode === 'dominant_bigfive_trait' || mode === 'residual_after_bigfive' || mode.startsWith('big5_');
    }

    function traitRegionsActive() {
      return currentDataset === 'roles' && currentProjection === 'pca' && currentView === '2d' && axisMap.x === 0 && axisMap.y === 1 && traitRegionLevel > 0;
    }

    function syncTraitRegionView() {
      currentDataset = 'roles';
      currentProjection = 'pca';
      currentView = '2d';
      axisMap.x = 0;
      axisMap.y = 1;
      axisMap.z = 2;
      currentCamera = null;
    }

    function activeTraitRegions() {
      const basis = TRAIT_REGION_OVERLAY.bases[traitRegionBasis] || TRAIT_REGION_OVERLAY.bases.quantile;
      return basis.cells || [];
    }

    function cleanTraitName(name) {
      return cleanLabel(name);
    }

    function traitListText(items, limit) {
      return (items || []).slice(0, limit).map(item => `${cleanTraitName(item.trait)}:${formatMaybe(item.score, 2)}`).join('; ');
    }

    function labelTextForRegion(region) {
      const names = (region.top_local_traits || []).slice(0, traitRegionLevel).map(item => cleanTraitName(item.trait));
      return names.join('<br>');
    }

    function regionHoverText(region) {
      return `<b>${region.basis_label}: ${region.pc1_band} / PC2 ${region.pc2_band}</b><br>n roles: ${region.role_count}${region.sparse_cell ? ' · SPARSE' : ''}<br>PC1: ${formatMaybe(region.pc1_min, 1)} to ${formatMaybe(region.pc1_max, 1)}<br>PC2: ${formatMaybe(region.pc2_min, 1)} to ${formatMaybe(region.pc2_max, 1)}<br>dominant cluster: ${region.dominant_cluster} (${formatMaybe(Number(region.dominant_cluster_fraction) * 100, 0)}%)<br><br>local enriched traits:<br>${traitListText(region.top_local_traits, 8)}<br><br>global comparison:<br>${traitListText(region.top_global_traits, 8)}<br><br>examples:<br>${(region.example_roles || []).map(cleanLabel).join(', ')}<extra></extra>`;
    }

    function regionForPoint(pc1, pc2) {
      return activeTraitRegions().find(region => pc1 >= region.pc1_min && pc1 <= region.pc1_max && pc2 >= region.pc2_min && pc2 <= region.pc2_max) || null;
    }

    function regionClusterForRole(name) {
      const ds = VIZ_DATA.roles;
      const idx = ds.names.indexOf(name);
      if (idx < 0 || !ds.pca3d) return 'unassigned';
      const region = regionForPoint(ds.pca3d[idx][0], ds.pca3d[idx][1]);
      return region ? region.dominant_cluster : 'unassigned';
    }

    function traitRegionAnnotations() {
      if (!traitRegionsActive()) return [];
      return activeTraitRegions().map(region => {
        const x = (region.pc1_min + region.pc1_max) / 2;
        const y = (region.pc2_min + region.pc2_max) / 2;
        const border = CLUSTER_COLORS[region.dominant_cluster] || '#666666';
        return {
          x, y,
          xref: 'x',
          yref: 'y',
          text: `${labelTextForRegion(region)}<br><span style="font-size:10px;color:#aaa">n=${region.role_count}${region.sparse_cell ? ' sparse' : ''}</span>`,
          showarrow: false,
          align: 'center',
          font: { size: 10, color: '#f2f2f2' },
          bgcolor: 'rgba(16,16,20,0.82)',
          bordercolor: border,
          borderwidth: 1,
          borderpad: 4,
          opacity: region.sparse_cell ? 0.62 : 0.92
        };
      });
    }

    function traitRegionShapes() {
      if (!traitRegionsActive()) return [];
      return activeTraitRegions().map(region => ({
        type: 'rect',
        xref: 'x',
        yref: 'y',
        x0: region.pc1_min,
        x1: region.pc1_max,
        y0: region.pc2_min,
        y1: region.pc2_max,
        line: {
          color: CLUSTER_COLORS[region.dominant_cluster] || '#666666',
          width: region.sparse_cell ? 1 : 1.4,
          dash: region.basis === 'explorer_grid' ? 'dot' : 'dash'
        },
        fillcolor: 'rgba(255,255,255,0.015)',
        layer: 'below'
      }));
    }

    function makeTraitRegionHoverTrace() {
      const regions = activeTraitRegions();
      return {
        type: 'scatter',
        mode: 'markers',
        name: 'trait-region hover',
        x: regions.map(region => (region.pc1_min + region.pc1_max) / 2),
        y: regions.map(region => (region.pc2_min + region.pc2_max) / 2),
        text: regions.map(regionHoverText),
        hovertemplate: '%{text}',
        customdata: regions.map(region => ({ kind: 'trait_region', region })),
        marker: { size: 42, color: 'rgba(255,255,255,0.01)', line: { width: 0 } },
        showlegend: false
      };
    }
""",
        "trait-region functions",
    )
    html = inject_once(
        html,
        "      if (!fixedRange || !ranges) {\n        note.classList.remove('active');\n        note.textContent = '';\n        return;\n      }",
        "      if (!fixedRange || !ranges) {\n        note.classList.remove('active');\n        note.textContent = '';\n        updateTraitRegionNote();\n        return;\n      }",
        "range note trait update",
    )
    html = inject_once(
        html,
        "      note.textContent = parts.join('  ');\n      note.classList.add('active');\n    }\n",
        "      note.textContent = parts.join('  ');\n      note.classList.add('active');\n      updateTraitRegionNote();\n    }\n\n    function updateTraitRegionNote() {\n      const note = document.getElementById('traitRegionNote');\n      if (!note) return;\n      if (!traitRegionsActive()) {\n        note.classList.remove('active');\n        note.textContent = '';\n        return;\n      }\n      const basis = TRAIT_REGION_OVERLAY.bases[traitRegionBasis] || TRAIT_REGION_OVERLAY.bases.quantile;\n      const sparse = activeTraitRegions().filter(region => region.sparse_cell).length;\n      note.textContent = `Trait-region overlay: ${basis.label}. Labels show top ${traitRegionLevel} PC1-band-relative Qwen trait-vector enrichments. Point geometry is unchanged. ${basis.description} ${sparse ? sparse + ' sparse cells flagged.' : 'No sparse cells flagged.'}`;\n      note.classList.add('active');\n    }\n",
        "trait-region note function",
    )
    html = inject_once(
        html,
        "      const sizes = markerSizes(ds);\n      const opacities = markerOpacities(ds);",
        "      if (traitRegionLevel > 0) syncTraitRegionView();\n      const sizes = markerSizes(ds);\n      const opacities = markerOpacities(ds);",
        "sync trait view in render",
    )
    html = inject_once(
        html,
        "      if (currentDataset === 'roles' && colorMode === 'cluster') {",
        "      if (traitRegionsActive()) traces.push(makeTraitRegionHoverTrace());\n\n      if (currentDataset === 'roles' && colorMode === 'trait_region_cluster') {\n        CLUSTER_ORDER.forEach(cluster => {\n          const idx = ds.names.map((_, i) => i).filter(i => regionClusterForRole(ds.names[i]) === cluster);\n          if (!idx.length) return;\n          traces.push(makeTrace(ds, coords, idx, {\n            name: `${cluster} region`,\n            color: CLUSTER_COLORS[cluster] || '#555555',\n            sizes,\n            opacities,\n            lines,\n            showscale: false\n          }));\n        });\n      } else if (currentDataset === 'roles' && colorMode === 'cluster') {",
        "trait region cluster color",
    )
    html = inject_once(
        html,
        "        layout.xaxis = axis2d(xAxisLabel, ranges?.x);\n        layout.yaxis = axis2d(yAxisLabel, ranges?.y);\n      }\n      Plotly.react('plot', traces, layout, { responsive: true, displayModeBar: true });",
        "        layout.xaxis = axis2d(xAxisLabel, ranges?.x);\n        layout.yaxis = axis2d(yAxisLabel, ranges?.y);\n        if (traitRegionsActive()) {\n          layout.shapes = traitRegionShapes();\n          layout.annotations = traitRegionAnnotations();\n        }\n      }\n      Plotly.react('plot', traces, layout, { responsive: true, displayModeBar: true });",
        "trait region layout",
    )
    html = inject_once(
        html,
        "      plot.on('plotly_hover', e => { if (!pinned) showPoint(e.points[0].customdata.idx, false); });",
        "      plot.on('plotly_hover', e => {\n        if (pinned || pinnedRegion) return;\n        const payload = e.points[0].customdata || {};\n        if (payload.kind === 'trait_region') showRegion(payload.region, false);\n        else showPoint(payload.idx, false);\n      });",
        "trait hover handler",
    )
    html = inject_once(
        html,
        "      plot.on('plotly_click', e => {\n        const idx = e.points[0].customdata.idx;\n        const name = ds.names[idx];",
        "      plot.on('plotly_click', e => {\n        const payload = e.points[0].customdata || {};\n        if (payload.kind === 'trait_region') {\n          pinnedRegion = payload.region;\n          pinned = null;\n          showRegion(payload.region, true);\n          return;\n        }\n        const idx = payload.idx;\n        const name = ds.names[idx];",
        "trait click handler",
    )
    html = inject_once(
        html,
        "        pinned = idx;\n        updateSelectionControls();",
        "        pinned = idx;\n        pinnedRegion = null;\n        updateSelectionControls();",
        "clear region pin on point click",
    )
    html = inject_once(
        html,
        "        const names = e.points.map(p => ds.names[p.customdata.idx]).filter(Boolean);",
        "        const names = e.points.filter(p => p.customdata && p.customdata.kind !== 'trait_region').map(p => ds.names[p.customdata.idx]).filter(Boolean);",
        "selection skips regions",
    )
    html = inject_once(
        html,
        "      const latest = lastSelectedPersona ? ds.names.indexOf(lastSelectedPersona) : -1;\n      if (latest >= 0) showPoint(latest, true);\n      else if (pinned !== null) showPoint(pinned, true);",
        "      const latest = lastSelectedPersona ? ds.names.indexOf(lastSelectedPersona) : -1;\n      if (pinnedRegion) showRegion(pinnedRegion, true);\n      else if (latest >= 0) showPoint(latest, true);\n      else if (pinned !== null) showPoint(pinned, true);",
        "render region pin",
    )
    html = inject_once(
        html,
        "        opacity: idx.map(i => opts.opacities[i]),",
        "        opacity: idx.map(i => traitRegionsActive() ? Math.min(opts.opacities[i], 0.48) : opts.opacities[i]),",
        "fade point opacity",
    )
    html = inject_once(
        html,
        "      pinned = null;\n      updateSelectionControls();",
        "      pinned = null;\n      pinnedRegion = null;\n      updateSelectionControls();",
        "clear region selection",
    )
    html = inject_once(
        html,
        "    function showPoint(i, isPinned) {\n      const ds = VIZ_DATA[currentDataset];",
        "    function showPoint(i, isPinned) {\n      document.getElementById('regionDetail').classList.remove('active');\n      const ds = VIZ_DATA[currentDataset];",
        "hide region detail on point",
    )
    html = inject_once(
        html,
        "    function renderLegend() {\n      const el = document.getElementById('legend');",
        "    function showRegion(region, isPinned) {\n      document.getElementById('selectedName').textContent = `${region.basis_label}: ${region.pc1_band} / PC2 ${region.pc2_band}`;\n      document.getElementById('selectedDataset').textContent = 'roles';\n      document.getElementById('selectedCluster').textContent = region.dominant_cluster;\n      document.getElementById('selectedAxis').textContent = '-';\n      document.getElementById('pinStatus').textContent = isPinned ? 'region pinned' : 'region preview';\n      const list = document.getElementById('neighbors');\n      list.innerHTML = '';\n      (region.example_roles || []).slice(0, 5).forEach(name => {\n        const li = document.createElement('li');\n        li.innerHTML = `<span class=\"name\">${cleanLabel(name)}</span><span class=\"cos\">example</span>`;\n        list.appendChild(li);\n      });\n      const detail = document.getElementById('regionDetail');\n      const body = document.getElementById('regionDetailBody');\n      const localChips = (region.top_local_traits || []).slice(0, traitRegionLevel || 3).map(item => `<span class=\"region-chip\">${cleanTraitName(item.trait)} ${formatMaybe(item.score, 2)}</span>`).join('');\n      body.innerHTML = `${localChips}<div class=\"region-text\">PC1 ${formatMaybe(region.pc1_min, 2)} to ${formatMaybe(region.pc1_max, 2)} · PC2 ${formatMaybe(region.pc2_min, 2)} to ${formatMaybe(region.pc2_max, 2)}<br>n=${region.role_count}${region.sparse_cell ? ' · sparse, descriptive only' : ''}<br>Global comparison: ${traitListText(region.top_global_traits, 5)}<br>${region.method_note}</div>`;\n      detail.classList.add('active');\n    }\n\n    function renderLegend() {\n      const el = document.getElementById('legend');",
        "show region function",
    )
    html = inject_once(
        html,
        "      if (currentDataset === 'roles' && colorMode === 'cluster') {",
        "      if (traitRegionsActive()) {\n        const basis = TRAIT_REGION_OVERLAY.bases[traitRegionBasis] || TRAIT_REGION_OVERLAY.bases.quantile;\n        const pointMeaning = colorMode === 'trait_region_cluster' ? 'active region dominant cluster' : colorMode === 'cluster' ? 'role cluster' : colorMode === 'axis' ? 'assistant-axis projection' : isBigFiveColorMode(colorMode) ? bigFiveColorTitle(colorMode) : 'selected point overlay';\n        el.innerHTML = `<span>Point color: ${pointMeaning}</span><span>Label text: top ${traitRegionLevel} locally enriched Qwen trait-vector cosines</span><span>Label border: dominant region cluster</span><span>Basis: ${basis.label}</span><span>Trait labels are same-space activation-cosine evidence, not independent ratings</span>`;\n        return;\n      }\n      if (currentDataset === 'roles' && colorMode === 'cluster') {",
        "trait legend",
    )

    EXPLORER.write_text(html)


def write_report(overlay: dict) -> None:
    quantile_sparse = sum(1 for c in overlay["bases"]["quantile"]["cells"] if c["sparse_cell"])
    explorer_sparse = sum(1 for c in overlay["bases"]["explorer_grid"]["cells"] if c["sparse_cell"])
    report = f"""# Trait-Region Overlay Integration Report

Generated UTC: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
Model used: GPT-5.5

## What Was Implemented

The existing `research/visualizations/persona_geometry_explorer.html` now has a native Qwen PC1 x PC2 trait-region overlay mode. The role scatterplot geometry is unchanged: the explorer still uses the existing embedded `VIZ_DATA.roles.pca3d` coordinates from `research/visualizations/geometry_viz_data.json`.

New controls:

- `Trait regions`: Off / Top 1 / Top 3 / Top 5.
- `Region basis`: Quantile bands / Explorer grid.
- `Color`: added `Region Cluster` as a point-color option for the active region basis.

When any trait-region level is selected, the explorer switches to Roles, PCA, 2D, PC1 on X and PC2 on Y. This prevents accidental overlays on UMAP or non-PC1/PC2 projections.

## Region Bases

Default: Quantile bands.

- Source: `research/outputs/qwen_pc2_trait_region_overlay/qwen_pc1_pc2_trait_region_cells.csv`
- Structure: 5 PC1 equal-count quantile bands x 3 within-band PC2 tertiles.
- Sparse cells: {quantile_sparse}.
- Interpretation: statistically stable default because cell sizes are controlled.

Secondary: Explorer grid.

- Source: recomputed from `research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv`
- Structure: 5 x 3 equal-width PC1 x PC2 grid in the explorer's PCA coordinate system.
- Sparse cells: {explorer_sparse}.
- Interpretation: better geometric alignment with the visible scatter coordinate system, but descriptive and less stable where sparse.

## Color Semantics

Point color remains controlled by the selected point-color mode. Label text always means top locally enriched Qwen trait-vector cosine labels. Label border color means the dominant role cluster inside that region. The implementation avoids using Assistant Axis colors for trait words unless `Axis Projection` is explicitly selected for points.

## Hover and Click Behavior

Hovering or clicking a region label/center shows:

- PC1 band and PC2 band.
- Role count.
- Top local trait enrichments and scores.
- Global-enrichment comparison.
- Dominant cluster.
- Example roles.

Role-point hover, click, selection, lasso/box selection, search highlighting, Big Five overlays, fixed range, and focus mode are preserved.

## Methodological Notes

Trait-region labels use PC1-band-relative enrichment by default, not global enrichment. They should be read as activation-space trait-vector cosine enrichments, not independent psychological ratings. This follows the provenance audit in `research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md`.

The overlay does not solve PC2. It is a native inspection mode for comparing local PC2 trait labels while preserving the original scatter geometry.

## Files

- Updated explorer: `research/visualizations/persona_geometry_explorer.html`
- Data bundle: `research/visualizations/trait_region_overlay_data.json`
- Integration script: `research/visualizations/run_integrate_trait_regions_into_explorer.py`
- Preview screenshot: `research/visualizations/trait_region_overlay_preview.png` if browser verification succeeds
"""
    REPORT_OUT.write_text(report)


def main() -> int:
    overlay = build_overlay_data()
    DATA_OUT.write_text(json.dumps(overlay, indent=2))
    update_explorer(overlay)
    write_report(overlay)
    print(f"Wrote {DATA_OUT.relative_to(ROOT)}")
    print(f"Updated {EXPLORER.relative_to(ROOT)}")
    print(f"Wrote {REPORT_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
