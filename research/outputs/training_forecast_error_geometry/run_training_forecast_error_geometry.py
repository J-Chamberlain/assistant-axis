#!/usr/bin/env python3
"""Visualize training-artifact forecast error geometry.

Compares original role/prompt-artifact target coordinates to frozen lightweight
forecaster predictions. This is the forecaster-native error field, not H100
response activation measurement.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

REPO = Path('/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis')
OUT = REPO / 'research/outputs/training_forecast_error_geometry'
OUT.mkdir(parents=True, exist_ok=True)

GEOMETRY = REPO / 'research/visualizations/geometry_viz_data.json'
ROLE_DIR = REPO / 'data/roles/instructions'
ROLE_LIST = REPO / 'data/roles/role_list.json'
FORECAST_DIR = REPO / 'research/outputs/prompt_to_geometry_forecasting'
FORECAST_RESULTS = FORECAST_DIR / 'forecasting_results.json'
FROZEN_MANIFEST = REPO / 'research/outputs/novel_prompt_battery/frozen_forecaster_manifest.json'
H100_ERRORS = REPO / 'research/outputs/h100_percentile_edge_validation_error_analysis/per_prompt_error_vectors.csv'
CHECKLIST = REPO / 'research/outputs/h100_diagnostic_followups/diagnostic_followup_checklist.md'
MODEL_USED = 'GPT-5.5'
EXPECTED_MODEL_HASH = '7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f'
TARGETS = ['PC1', 'PC2', 'PC3']


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def normalize_space(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def remove_label(text: str, name: str) -> str:
    variants = {name, name.replace('_', ' '), name.replace('_', '-'), name.replace('-', ' ')}
    out = text
    for variant in sorted(variants, key=len, reverse=True):
        if not variant:
            continue
        pattern = re.compile(rf'\b{re.escape(variant)}s?\b', re.IGNORECASE)
        out = pattern.sub('[TARGET]', out)
    return out


def prompt_parts(obj: dict[str, Any], description: str) -> list[str]:
    parts = []
    if description:
        parts.append(f'Description: {description}')
    for idx, item in enumerate(obj.get('instruction', [])):
        if item.get('pos'):
            parts.append(f'Positive instruction {idx}: {item["pos"]}')
    if obj.get('questions'):
        parts.append('Behavioral questions: ' + ' '.join(str(q) for q in obj['questions']))
    return parts


def model_sha(model: Any) -> str:
    tfidf = model.named_steps['tfidf']
    estimator = model.named_steps['model']
    payload = {
        'vocabulary': sorted((str(k), int(v)) for k, v in tfidf.vocabulary_.items()),
        'idf': np.round(tfidf.idf_, 10).tolist(),
        'coef': [np.round(est.coef_, 10).tolist() for est in estimator.estimators_],
        'intercept': [np.round(np.atleast_1d(est.intercept_), 10).tolist() for est in estimator.estimators_],
        'config': {
            'ngram_range': [1, 2],
            'max_features': 6000,
            'alpha': 0.01,
            'l1_ratio': 0.25,
            'random_state': 42,
        },
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load_role_targets() -> pd.DataFrame:
    geom = load_json(GEOMETRY)['roles']
    df = pd.DataFrame(geom['pca3d'], columns=['target_pc1', 'target_pc2', 'target_pc3'])
    df['role_name'] = geom['names']
    df['cluster'] = geom.get('clusters', ['unassigned'] * len(df))
    return df.set_index('role_name')


def build_role_examples() -> pd.DataFrame:
    descriptions = load_json(ROLE_LIST)
    targets = load_role_targets()
    results = load_json(FORECAST_RESULTS)
    prior_holdouts = set(results.get('role_holdout_names', []))
    rows = []
    for path in sorted(ROLE_DIR.glob('*.json')):
        name = path.stem
        if name == 'default' or name not in targets.index:
            continue
        obj = load_json(path)
        raw_text = normalize_space('\n'.join(prompt_parts(obj, descriptions.get(name, ''))))
        text = remove_label(raw_text, name)
        target = targets.loc[name]
        rows.append({
            'prompt_id': f'role_artifact_{name}',
            'concept_type': 'role',
            'role_name': name,
            'concept_name': name,
            'split': 'heldout_role_prior' if name in prior_holdouts else 'train_prior',
            'prompt_text': text,
            'prompt_text_excerpt': text[:240],
            'prompt_source_fields': 'role description + positive instructions + behavioral questions; eval prompts excluded; explicit role label replaced by [TARGET]',
            'role_labels_excluded': True,
            'cluster': target['cluster'],
            'target_pc1': float(target['target_pc1']),
            'target_pc2': float(target['target_pc2']),
            'target_pc3': float(target['target_pc3']),
        })
    return pd.DataFrame(rows)


def add_predictions(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    manifest = load_json(FROZEN_MANIFEST)
    model_path = REPO / manifest['model_path']
    model = joblib.load(model_path)
    stable_hash = model_sha(model)
    joblib_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if stable_hash != EXPECTED_MODEL_HASH:
        raise RuntimeError(f'model hash mismatch: {stable_hash} != {EXPECTED_MODEL_HASH}')
    pred = np.asarray(model.predict(df['prompt_text'].tolist()), dtype=float)
    for idx, pc in enumerate(['pc1', 'pc2', 'pc3']):
        df[f'forecast_{pc}'] = pred[:, idx]
        df[f'delta_{pc}'] = df[f'forecast_{pc}'] - df[f'target_{pc}']
    df['euclidean_delta_3d'] = np.sqrt(df['delta_pc1']**2 + df['delta_pc2']**2 + df['delta_pc3']**2)
    df['target_radius_from_origin'] = np.sqrt(df['target_pc1']**2 + df['target_pc2']**2 + df['target_pc3']**2)
    df['forecast_radius_from_origin'] = np.sqrt(df['forecast_pc1']**2 + df['forecast_pc2']**2 + df['forecast_pc3']**2)
    df['radial_movement_toward_origin'] = df['target_radius_from_origin'] - df['forecast_radius_from_origin']
    df['forecast_closer_to_origin'] = df['forecast_radius_from_origin'] < df['target_radius_from_origin']
    df['forecast_pc3_near_zero_abs5'] = df['forecast_pc3'].abs() <= 5.0
    df['forecast_pc3_near_zero_abs2'] = df['forecast_pc3'].abs() <= 2.0
    df['model_used'] = MODEL_USED
    df['forecasting_model_hash'] = stable_hash
    return df, {
        'manifest': manifest,
        'model_path': manifest['model_path'],
        'model_hash': stable_hash,
        'serialized_joblib_sha256': joblib_hash,
    }


def axis_metrics(df: pd.DataFrame, scope_col: str = 'all') -> dict[str, Any]:
    out = {}
    for pc in ['pc1', 'pc2', 'pc3']:
        y = df[f'target_{pc}'].to_numpy(float)
        pred = df[f'forecast_{pc}'].to_numpy(float)
        delta = pred - y
        out[pc] = {
            'r2': float(r2_score(y, pred)),
            'pearson': float(pearsonr(y, pred).statistic),
            'spearman': float(spearmanr(y, pred).statistic),
            'rmse': float(math.sqrt(mean_squared_error(y, pred))),
            'mae': float(mean_absolute_error(y, pred)),
            'signed_bias_mean_delta': float(delta.mean()),
            'signed_bias_median_delta': float(np.median(delta)),
        }
    out['euclidean_delta_3d_mean'] = float(df['euclidean_delta_3d'].mean())
    out['euclidean_delta_3d_median'] = float(df['euclidean_delta_3d'].median())
    out['forecast_closer_to_origin_fraction'] = float(df['forecast_closer_to_origin'].mean())
    out['mean_radial_movement_toward_origin'] = float(df['radial_movement_toward_origin'].mean())
    out['forecast_pc3_abs_le_5_fraction'] = float(df['forecast_pc3_near_zero_abs5'].mean())
    out['forecast_pc3_abs_le_2_fraction'] = float(df['forecast_pc3_near_zero_abs2'].mean())
    out['n'] = int(len(df))
    return out


def summarize_errors(df: pd.DataFrame, model_info: dict[str, Any]) -> dict[str, Any]:
    summary = {
        'model_used': MODEL_USED,
        'predictions_loaded_or_recomputed': 'recomputed from frozen serialized role-trained leakage-control elastic-net TF-IDF forecaster; no saved per-example role prediction table was present',
        'forecasting_model_used': 'role-trained leakage-control elastic-net TF-IDF',
        'forecasting_model_hash': model_info['model_hash'],
        'expected_model_hash': EXPECTED_MODEL_HASH,
        'serialized_joblib_sha256': model_info['serialized_joblib_sha256'],
        'input_text_fields': 'role description + positive instructions + behavioral questions',
        'role_labels_excluded': True,
        'eval_prompts_excluded': True,
        'n_examples': int(len(df)),
        'split_counts': df['split'].value_counts().to_dict(),
        'global': axis_metrics(df),
        'by_split': {split: axis_metrics(sub) for split, sub in df.groupby('split')},
        'by_cluster': {cluster: axis_metrics(sub) for cluster, sub in df.groupby('cluster')},
    }
    if H100_ERRORS.exists():
        h = pd.read_csv(H100_ERRORS)
        h_summary = {
            'n': int(len(h)),
            'mean_euclidean_delta_3d': float(h['euclidean_delta_3d'].mean()),
            'median_euclidean_delta_3d': float(h['euclidean_delta_3d'].median()),
            'mean_delta_pc1_observed_minus_forecast': float(h['delta_pc1'].mean()),
            'mean_delta_pc2_observed_minus_forecast': float(h['delta_pc2'].mean()),
            'mean_delta_pc3_observed_minus_forecast': float(h['delta_pc3'].mean()),
            'forecast_pc3_abs_le_5_fraction': float((h['predicted_pc3'].abs() <= 5.0).mean()),
            'forecast_pc3_abs_le_2_fraction': float((h['predicted_pc3'].abs() <= 2.0).mean()),
            'center_collapse_fraction': float(h['center_collapse'].mean()) if 'center_collapse' in h else None,
        }
        summary['h100_comparison'] = h_summary
        summary['h100_error_larger_than_training_native'] = bool(h_summary['mean_euclidean_delta_3d'] > summary['global']['euclidean_delta_3d_mean'])
        summary['pc2_upward_shift_native_mean_delta_forecast_minus_target'] = summary['global']['pc2']['signed_bias_mean_delta']
        summary['pc2_upward_shift_h100_mean_delta_observed_minus_forecast'] = h_summary['mean_delta_pc2_observed_minus_forecast']
        summary['pc2_upward_shift_interpretation'] = 'native_forecaster_already_upward' if summary['global']['pc2']['signed_bias_mean_delta'] > 0 else 'h100_specific_or_response_measurement_shift'
    return summary


def color_value(row: dict[str, Any], mode: str):
    if mode == 'split':
        return row['split']
    if mode == 'cluster':
        return row['cluster']
    if mode == 'error':
        return row['euclidean_delta_3d']
    if mode in {'delta_pc1', 'delta_pc2', 'delta_pc3'}:
        return row[mode]
    return row['split']


def make_hover(row: dict[str, Any]) -> str:
    return (
        f"<b>{row['concept_name']}</b><br>split={row['split']}<br>cluster={row['cluster']}"
        f"<br>target=({row['target_pc1']:.2f}, {row['target_pc2']:.2f}, {row['target_pc3']:.2f})"
        f"<br>forecast=({row['forecast_pc1']:.2f}, {row['forecast_pc2']:.2f}, {row['forecast_pc3']:.2f})"
        f"<br>delta=({row['delta_pc1']:.2f}, {row['delta_pc2']:.2f}, {row['delta_pc3']:.2f})"
        f"<br>|delta|={row['euclidean_delta_3d']:.2f}<br>{row['prompt_text_excerpt']}"
    )


def html_template(title: str, data: list[dict[str, Any]], background: list[dict[str, Any]], dims: tuple[str, str, str] | tuple[str, str], mode3d: bool) -> str:
    data_json = json.dumps(data)
    bg_json = json.dumps(background)
    dims_json = json.dumps(dims)
    plot_type = '3d' if mode3d else '2d'
    return f'''<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
body {{ margin:0; background:#0a0a12; color:#ddd; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
header {{ padding:14px 18px; border-bottom:1px solid #252536; }}
h1 {{ font-size:17px; margin:0 0 8px; font-weight:600; }}
.controls {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; font-size:12px; color:#aaa; }}
select,label {{ background:#12121b; color:#ddd; border:1px solid #333348; padding:4px 6px; }}
label {{ border:none; }}
#plot {{ width:100vw; height:calc(100vh - 88px); }}
.note {{ color:#777; font-size:11px; }}
</style></head><body>
<header><h1>{title}</h1>
<div class="controls">
<span>Filter</span><select id="filter"><option value="all">all</option><option value="train_prior">train only</option><option value="heldout_role_prior">held-out only</option><option value="role">role artifacts only</option></select>
<span>Color</span><select id="color"><option value="split">split</option><option value="cluster">cluster</option><option value="error">error magnitude</option><option value="delta_pc1">PC1 signed error</option><option value="delta_pc2">PC2 signed error</option><option value="delta_pc3">PC3 signed error</option></select>
<label><input type="checkbox" id="background" checked> background</label>
<label><input type="checkbox" id="targets" checked> targets</label>
<label><input type="checkbox" id="forecasts" checked> forecasts</label>
<label><input type="checkbox" id="arrows" checked> arrows</label>
<span class="note">Arrow direction: target -> forecast</span>
</div></header><div id="plot"></div>
<script>
const DATA = {data_json};
const BG = {bg_json};
const DIMS = {dims_json};
const MODE = '{plot_type}';
const CLUSTER_COLORS = {{editorial:'#e8b84b', procedural_professional:'#4a9eff', grounded_social:'#5ecb8a', other:'#b0b0b0', combative_iconoclast:'#ff6b6b', mythic_spiritual:'#c084fc', trickster_chaos:'#fb923c', unassigned:'#555'}};
const SPLIT_COLORS = {{train_prior:'#4a9eff', heldout_role_prior:'#ffb74d'}};
function getRows() {{ const f=document.getElementById('filter').value; return DATA.filter(r => f==='all' || f==='role' || r.split===f); }}
function markerColors(rows, mode) {{
  if (mode==='split') return rows.map(r => SPLIT_COLORS[r.split] || '#ddd');
  if (mode==='cluster') return rows.map(r => CLUSTER_COLORS[r.cluster] || '#ddd');
  if (mode==='error') return rows.map(r => r.euclidean_delta_3d);
  return rows.map(r => r[mode]);
}}
function colorScale(mode) {{ return ['error','delta_pc1','delta_pc2','delta_pc3'].includes(mode) ? 'RdBu' : null; }}
function traceScatter(name, rows, prefix, size, symbol) {{
  const mode = document.getElementById('color').value;
  const colors = markerColors(rows, mode);
  const cs = colorScale(mode);
  const common = {{name, mode:'markers', text: rows.map(r=>r.hover), hoverinfo:'text', marker:{{size, color:colors, opacity:0.86, symbol}} }};
  if (cs) {{ common.marker.colorscale=cs; common.marker.showscale=true; common.marker.colorbar={{title:mode}}; }}
  if (MODE==='3d') {{ return {{type:'scatter3d', x:rows.map(r=>r[prefix+'_pc1']), y:rows.map(r=>r[prefix+'_pc2']), z:rows.map(r=>r[prefix+'_pc3']), ...common}}; }}
  return {{type:'scatter', x:rows.map(r=>r[prefix+'_'+DIMS[0].toLowerCase()]), y:rows.map(r=>r[prefix+'_'+DIMS[1].toLowerCase()]), ...common}};
}}
function arrowTrace(rows) {{
  const xs=[], ys=[], zs=[];
  for (const r of rows) {{
    if (MODE==='3d') {{ xs.push(r.target_pc1, r.forecast_pc1, null); ys.push(r.target_pc2, r.forecast_pc2, null); zs.push(r.target_pc3, r.forecast_pc3, null); }}
    else {{ const a=DIMS[0].toLowerCase(), b=DIMS[1].toLowerCase(); xs.push(r['target_'+a], r['forecast_'+a], null); ys.push(r['target_'+b], r['forecast_'+b], null); }}
  }}
  if (MODE==='3d') return {{type:'scatter3d', mode:'lines', name:'target -> forecast', x:xs, y:ys, z:zs, hoverinfo:'skip', line:{{color:'rgba(255,255,255,0.28)', width:2}}}};
  return {{type:'scatter', mode:'lines', name:'target -> forecast', x:xs, y:ys, hoverinfo:'skip', line:{{color:'rgba(255,255,255,0.30)', width:1}}}};
}}
function backgroundTrace() {{
  if (MODE==='3d') return {{type:'scatter3d', mode:'markers', name:'inherited persona geometry', x:BG.map(r=>r.pc1), y:BG.map(r=>r.pc2), z:BG.map(r=>r.pc3), hovertext:BG.map(r=>r.name), hoverinfo:'text', marker:{{size:2.5, color:'rgba(180,180,190,0.20)'}}}};
  return {{type:'scatter', mode:'markers', name:'inherited persona geometry', x:BG.map(r=>r[DIMS[0].toLowerCase()]), y:BG.map(r=>r[DIMS[1].toLowerCase()]), hovertext:BG.map(r=>r.name), hoverinfo:'text', marker:{{size:3, color:'rgba(180,180,190,0.20)'}}}};
}}
function render() {{
  const rows=getRows(); const traces=[];
  if (document.getElementById('background').checked) traces.push(backgroundTrace());
  if (document.getElementById('arrows').checked) traces.push(arrowTrace(rows));
  if (document.getElementById('targets').checked) traces.push(traceScatter('target persona coordinate', rows, 'target', MODE==='3d'?4:6, 'circle'));
  if (document.getElementById('forecasts').checked) traces.push(traceScatter('forecast coordinate', rows, 'forecast', MODE==='3d'?4:6, 'diamond'));
  const layout = {{paper_bgcolor:'#0a0a12', plot_bgcolor:'#0a0a12', font:{{color:'#ddd', family:'monospace'}}, margin:{{l:50,r:20,t:20,b:50}}, legend:{{orientation:'h'}}}};
  if (MODE==='3d') layout.scene={{xaxis:{{title:'PC1'}}, yaxis:{{title:'PC2'}}, zaxis:{{title:'PC3'}}, bgcolor:'#0a0a12'}};
  else {{ layout.xaxis={{title:DIMS[0], gridcolor:'#20202c', zerolinecolor:'#555'}}; layout.yaxis={{title:DIMS[1], gridcolor:'#20202c', zerolinecolor:'#555'}}; }}
  Plotly.react('plot', traces, layout, {{responsive:true}});
}}
for (const id of ['filter','color','background','targets','forecasts','arrows']) document.getElementById(id).addEventListener('change', render);
render();
</script></body></html>'''


def write_htmls(df: pd.DataFrame):
    rows = []
    for rec in df.to_dict('records'):
        rec = {k: (None if pd.isna(v) else v) for k, v in rec.items()}
        rec['hover'] = make_hover(rec)
        rows.append(rec)
    geom = load_json(GEOMETRY)['roles']
    bg = [
        {'name': name, 'pc1': coords[0], 'pc2': coords[1], 'pc3': coords[2], 'cluster': cluster}
        for name, coords, cluster in zip(geom['names'], geom['pca3d'], geom.get('clusters', []))
    ]
    (OUT / 'training_forecast_error_3d_arrows.html').write_text(html_template('Training Forecast Error Geometry - 3D Target to Forecast', rows, bg, ('PC1','PC2','PC3'), True))
    (OUT / 'training_forecast_error_2d_arrows_pc1_pc2.html').write_text(html_template('Training Forecast Error Geometry - PC1 vs PC2', rows, bg, ('PC1','PC2'), False))
    (OUT / 'training_forecast_error_2d_arrows_pc1_pc3.html').write_text(html_template('Training Forecast Error Geometry - PC1 vs PC3', rows, bg, ('PC1','PC3'), False))
    (OUT / 'training_forecast_error_2d_arrows_pc2_pc3.html').write_text(html_template('Training Forecast Error Geometry - PC2 vs PC3', rows, bg, ('PC2','PC3'), False))


def write_report(summary: dict[str, Any]):
    g = summary['global']; h = summary.get('h100_comparison', {})
    lines = [
        '# Training Forecast Error Geometry', '',
        f"model_used: {MODEL_USED}", '',
        '## Forecasting Model', '',
        '- Exact model: role-trained leakage-control elastic-net TF-IDF',
        f"- Model hash: `{summary['forecasting_model_hash']}`",
        '- Predictions were recomputed from the frozen serialized forecaster because no saved per-example role prediction table existed.',
        '- Important split caveat: the frozen design forecaster was retrained on all 275 role artifacts, so `heldout_role_prior` marks the prior validation split membership but is not out-of-sample for this frozen-model visualization.',
        '- Input text fields: role description + positive instructions + behavioral questions.',
        '- Role labels excluded: yes, explicit role names replaced by `[TARGET]`.',
        '- Eval prompts excluded: yes.', '',
        '## Counts', '',
        f"- Examples visualized: {summary['n_examples']}",
        f"- Split counts: `{summary['split_counts']}`", '',
        '## Target-to-Forecast Metrics', '',
        '| axis | R2 | Pearson | Spearman | RMSE | MAE | signed bias mean |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for pc in ['pc1','pc2','pc3']:
        m = g[pc]
        lines.append(f"| {pc.upper()} | {m['r2']:.3f} | {m['pearson']:.3f} | {m['spearman']:.3f} | {m['rmse']:.3f} | {m['mae']:.3f} | {m['signed_bias_mean_delta']:.3f} |")
    lines += ['', '## Native Error Geometry', '',
        f"- Mean 3D error: {g['euclidean_delta_3d_mean']:.3f}",
        f"- Median 3D error: {g['euclidean_delta_3d_median']:.3f}",
        f"- Forecast closer to origin fraction: {g['forecast_closer_to_origin_fraction']:.3f}",
        f"- Mean radial movement toward origin: {g['mean_radial_movement_toward_origin']:.3f}",
        f"- Forecast |PC3| <= 5 fraction: {g['forecast_pc3_abs_le_5_fraction']:.3f}",
        f"- Forecast |PC3| <= 2 fraction: {g['forecast_pc3_abs_le_2_fraction']:.3f}", '',
    ]
    if h:
        lines += ['## Comparison To H100 Forecast-Observed Error', '',
            f"- H100 mean 3D error: {h['mean_euclidean_delta_3d']:.3f} vs native training-artifact mean 3D error {g['euclidean_delta_3d_mean']:.3f}.",
            f"- H100 signed deltas observed-minus-forecast: PC1 {h['mean_delta_pc1_observed_minus_forecast']:.3f}, PC2 {h['mean_delta_pc2_observed_minus_forecast']:.3f}, PC3 {h['mean_delta_pc3_observed_minus_forecast']:.3f}.",
            f"- Native signed deltas forecast-minus-target: PC1 {g['pc1']['signed_bias_mean_delta']:.3f}, PC2 {g['pc2']['signed_bias_mean_delta']:.3f}, PC3 {g['pc3']['signed_bias_mean_delta']:.3f}.",
            f"- H100 forecast |PC3| <= 5 fraction: {h['forecast_pc3_abs_le_5_fraction']:.3f}; native artifact forecast |PC3| <= 5 fraction: {g['forecast_pc3_abs_le_5_fraction']:.3f}.", '',
        ]
    pc2_native = g['pc2']['signed_bias_mean_delta']
    h100_pc2 = h.get('mean_delta_pc2_observed_minus_forecast')
    if h100_pc2 is not None and h100_pc2 > 0 and pc2_native <= 0:
        pc2_line = 'The H100 PC2 upward shift is not present in the original target-to-forecast comparison; it appears during response generation/activation measurement rather than in the native forecaster.'
    elif h100_pc2 is not None and h100_pc2 > 0 and pc2_native > 0:
        pc2_line = 'The H100 PC2 upward shift overlaps with a native upward PC2 forecaster bias, so the response-state effect is not cleanly separable without further calibration.'
    else:
        pc2_line = 'PC2 shift comparison is inconclusive from the available H100 summary.'
    pc3_line = 'The suspicious PC3 near-zero forecast clustering is present in the original artifact predictions.' if g['forecast_pc3_abs_le_5_fraction'] > 0.5 else 'The suspicious PC3 near-zero forecast clustering is not dominant in the original role-artifact predictions.'
    origin_line = 'The forecaster has native origin/centroid bias.' if g['forecast_closer_to_origin_fraction'] > 0.5 and g['mean_radial_movement_toward_origin'] > 0 else 'The forecaster does not show a dominant native pull toward the origin on role artifacts.'
    lines += ['## Conclusions', '',
        f'- {origin_line}',
        f'- {pc3_line}',
        f'- {pc2_line}',
        '- Recommended next diagnostic step: run the same target-to-forecast visualization for held-out-role-only models and compare against the frozen all-role design forecaster to separate in-sample shrinkage from generalization error.', '',
    ]
    (OUT / 'training_forecast_error_report.md').write_text('\n'.join(lines))


def update_checklist(summary: dict[str, Any]):
    if not CHECKLIST.exists():
        return
    text = CHECKLIST.read_text()
    marker = '## 2026-05-31 Training forecast error geometry update'
    block = f'''

{marker}

- D03 forecasted extreme-PC1 / near-zero-PC3 prompts: compare H100 cases against `research/outputs/training_forecast_error_geometry/training_forecast_error_3d_arrows.html` to determine whether near-zero PC3 forecasts are already present in native role-artifact forecaster predictions.
- D08 prompt-generation loop forecaster exploitation or origin bias: use `training_forecast_per_example_errors.csv` and the 2D arrow views to separate native forecaster shrinkage from prompt-generation loop artifacts.
- D09 calibration failure versus directional failure: native target-to-forecast signed bias and H100 observed-minus-forecast signed bias are now directly comparable in `training_forecast_error_summary.json`.
'''
    if marker not in text:
        CHECKLIST.write_text(text.rstrip() + block)


def main():
    df = build_role_examples()
    df, model_info = add_predictions(df)
    df.to_csv(OUT / 'training_forecast_per_example_errors.csv', index=False)
    summary = summarize_errors(df, model_info)
    (OUT / 'training_forecast_error_summary.json').write_text(json.dumps(summary, indent=2))
    write_htmls(df)
    write_report(summary)
    update_checklist(summary)
    print((OUT / 'training_forecast_error_report.md').read_text())

if __name__ == '__main__':
    main()
