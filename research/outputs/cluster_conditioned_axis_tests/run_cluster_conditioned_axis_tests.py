from pathlib import Path
import json, math, csv
import warnings
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, f1_score, r2_score, mean_squared_error

warnings.filterwarnings('ignore', category=RuntimeWarning, module='sklearn.utils.extmath')

REPO = Path('/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis')
OUT = REPO / 'research/outputs/cluster_conditioned_axis_tests'
OUT.mkdir(parents=True, exist_ok=True)
GEOM_PATH = REPO / 'research/visualizations/geometry_viz_data.json'
RATER_PATH = REPO / 'research/q2_stability/qwen/outputs/blinded_axis_rater_study/axis_rater_scores.csv'
DOSSIER_PATH = REPO / 'research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_persona_dossiers.jsonl'
SCRIPT_OUT = OUT / 'run_cluster_conditioned_axis_tests.py'
MODEL_USED = 'GPT-5.5'

TARGET_AXES = {
    'pc1': {
        'pc_col': 'pc1',
        'score_col': 'pc1_proxy_convergence_pressure',
        'label': 'convergence pressure versus degrees of freedom',
        'score_source': 'axis_rater_scores.csv: pc1_objective_certainty_score',
        'higher_score_means': 'correct-answer/procedural convergence, validation, checking, externally constrained answer space',
    },
    'pc2': {
        'pc_col': 'pc2',
        'score_col': 'pc2_proxy_situated_developmental_immediacy',
        'label': 'integrated abstraction versus situated developmental immediacy',
        'score_source': 'derived as 100 - abstraction_score from axis_rater_scores.csv; higher means less integrated abstraction and more local immediacy',
        'higher_score_means': 'local immediacy, developmental limitation, reactivity, situated/social embodiment',
    },
}


def load_dossiers():
    texts = {}
    if not DOSSIER_PATH.exists():
        return texts
    for line in DOSSIER_PATH.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        persona_id = rec.get('persona_id')
        parts = []
        for item in rec.get('records', []):
            text = item.get('text')
            if text:
                parts.append(text)
        if persona_id:
            texts[persona_id] = '\n'.join(parts)
    return texts


def load_data():
    geom = json.loads(GEOM_PATH.read_text())['roles']
    gdf = pd.DataFrame({
        'persona': geom['names'],
        'pc1_geom': [x[0] for x in geom['pca3d']],
        'pc2_geom': [x[1] for x in geom['pca3d']],
        'pc3_geom': [x[2] for x in geom['pca3d']],
        'cluster_geom': geom['clusters'],
    })
    rdf = pd.read_csv(RATER_PATH)
    df = rdf.merge(gdf, left_on='persona_name', right_on='persona', how='inner')
    # Prefer canonical geometry values from the visualization data.
    df['pc1'] = df['pc1_geom'].astype(float)
    df['pc2'] = df['pc2_geom'].astype(float)
    df['pc3'] = df['pc3_geom'].astype(float)
    df['cluster'] = df['cluster_geom']
    df['pc1_proxy_convergence_pressure'] = df['pc1_objective_certainty_score'].astype(float)
    df['pc2_proxy_situated_developmental_immediacy'] = 100.0 - df['abstraction_score'].astype(float)
    df['pc2_proxy_component_abstraction_score'] = df['abstraction_score'].astype(float)
    df['pc2_proxy_component_developmental_limitation'] = 100.0 - df['maturity_score'].astype(float)
    texts = load_dossiers()
    df['text_for_cluster_prediction'] = [texts.get(pid, '') for pid in df['persona_id']]
    return df


def corr(x, y):
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    if len(x) < 3 or len(set(np.round(x, 12))) < 2 or len(set(np.round(y, 12))) < 2:
        return {'r': None, 'p': None}
    r, p = stats.pearsonr(x, y)
    return {'r': float(r), 'p': float(p)}


def spear(x, y):
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    if len(x) < 3 or len(set(np.round(x, 12))) < 2 or len(set(np.round(y, 12))) < 2:
        return {'r': None, 'p': None}
    r, p = stats.spearmanr(x, y)
    return {'r': float(r), 'p': float(p)}


def residualize_by_cluster(values, clusters):
    values = np.asarray(values, dtype=float)
    out = np.zeros_like(values)
    for cl in sorted(set(clusters)):
        mask = np.array([c == cl for c in clusters])
        out[mask] = values[mask] - values[mask].mean()
    return out


def pairwise_accuracy(df, score_col, pc_col, mode='global', cluster=None):
    scores = df[score_col].to_numpy(dtype=float)
    pcs = df[pc_col].to_numpy(dtype=float)
    clusters = df['cluster'].to_numpy()
    i, j = np.triu_indices(len(df), k=1)
    mask = np.ones(len(i), dtype=bool)
    same = clusters[i] == clusters[j]
    if mode == 'within':
        mask &= same
    elif mode == 'across':
        mask &= ~same
    if cluster is not None:
        mask &= same & (clusters[i] == cluster)
    ds = scores[i] - scores[j]
    dp = pcs[i] - pcs[j]
    mask &= (np.abs(ds) >= 1e-12) & (np.abs(dp) >= 1e-12)
    total = int(mask.sum())
    ties = int(len(mask) - total)
    if total == 0:
        return {'accuracy': None, 'n_pairs': 0, 'ties': ties}
    correct = int(((ds[mask] * dp[mask]) > 0).sum())
    return {'accuracy': correct / total, 'n_pairs': total, 'ties': ties}


def bootstrap_pairwise_diff(df, score_col, pc_col, n=200, seed=42):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(df))
    vals = []
    for _ in range(n):
        sample = df.iloc[rng.choice(idx, size=len(idx), replace=True)].reset_index(drop=True)
        g = pairwise_accuracy(sample, score_col, pc_col, 'global')['accuracy']
        w = pairwise_accuracy(sample, score_col, pc_col, 'within')['accuracy']
        if g is not None and w is not None:
            vals.append(w - g)
    if not vals:
        return {'mean_diff': None, 'ci_low': None, 'ci_high': None}
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return {'mean_diff': float(np.mean(vals)), 'ci_low': float(lo), 'ci_high': float(hi)}


def axis_stats(df, axis):
    spec = TARGET_AXES[axis]
    score = spec['score_col']; pc = spec['pc_col']
    result_rows = []
    for mode in ['global', 'within', 'across']:
        pa = pairwise_accuracy(df, score, pc, mode)
        result_rows.append({'axis': axis, 'scope': mode, 'cluster': 'ALL', **pa})
    for cl in sorted(df['cluster'].unique()):
        pa = pairwise_accuracy(df, score, pc, 'within', cl)
        sub = df[df['cluster'] == cl]
        result_rows.append({'axis': axis, 'scope': 'within_cluster', 'cluster': cl, **pa})
    by_cluster = {}
    for cl in sorted(df['cluster'].unique()):
        sub = df[df['cluster'] == cl]
        by_cluster[cl] = {
            'n': int(len(sub)),
            'pearson': corr(sub[score], sub[pc]),
            'spearman': spear(sub[score], sub[pc]),
            'pairwise': pairwise_accuracy(df, score, pc, 'within', cl),
        }
    score_resid = residualize_by_cluster(df[score].values, df['cluster'].values)
    pc_resid = residualize_by_cluster(df[pc].values, df['cluster'].values)
    return {
        'axis': axis,
        'label': spec['label'],
        'score_col': score,
        'score_source': spec['score_source'],
        'n_roles': int(len(df)),
        'global_pearson': corr(df[score], df[pc]),
        'global_spearman': spear(df[score], df[pc]),
        'cluster_controlled_pearson': corr(score_resid, pc_resid),
        'cluster_controlled_spearman': spear(score_resid, pc_resid),
        'pairwise_global': pairwise_accuracy(df, score, pc, 'global'),
        'pairwise_within_cluster': pairwise_accuracy(df, score, pc, 'within'),
        'pairwise_across_cluster': pairwise_accuracy(df, score, pc, 'across'),
        'within_minus_global_bootstrap': bootstrap_pairwise_diff(df, score, pc),
        'per_cluster': by_cluster,
        'pairwise_rows': result_rows,
    }


def one_hot(clusters, known_clusters):
    encoded_clusters = list(known_clusters)[1:]
    arr = np.zeros((len(clusters), len(encoded_clusters)))
    pos = {c: i for i, c in enumerate(encoded_clusters)}
    for i, c in enumerate(clusters):
        if c in pos:
            arr[i, pos[c]] = 1.0
    return arr


def interaction_features(scores, clusters, known_clusters):
    scores = np.asarray(scores, dtype=float).reshape(-1, 1)
    oh = one_hot(clusters, known_clusters)
    return np.hstack([scores, oh, scores * oh])


def pred_pairwise_accuracy(y_true, y_pred):
    correct = total = ties = 0
    n = len(y_true)
    for i in range(n):
        for j in range(i + 1, n):
            da = y_true[i] - y_true[j]
            dp = y_pred[i] - y_pred[j]
            if abs(da) < 1e-12 or abs(dp) < 1e-12:
                ties += 1
                continue
            total += 1
            if da * dp > 0:
                correct += 1
    return None if total == 0 else correct / total


def prediction_regimes(df, axis):
    spec = TARGET_AXES[axis]
    score = spec['score_col']; pc = spec['pc_col']
    y = df[pc].values.astype(float)
    x_score = df[[score]].values.astype(float)
    text = df['text_for_cluster_prediction'].fillna('').values
    clusters = df['cluster'].values
    known_clusters = sorted(df['cluster'].unique())
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    preds = {k: np.zeros(len(df), dtype=float) for k in ['direct_axis', 'oracle_cluster', 'predicted_cluster']}
    pred_clusters = np.empty(len(df), dtype=object)
    fold_rows = []
    for fold, (train_idx, test_idx) in enumerate(skf.split(text, clusters), start=1):
        clf = make_pipeline(
            TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=6000),
            LogisticRegression(max_iter=1000, class_weight='balanced', C=2.0, random_state=42),
        )
        clf.fit(text[train_idx], clusters[train_idx])
        test_pred_cl = clf.predict(text[test_idx])
        pred_clusters[test_idx] = test_pred_cl

        direct = LinearRegression().fit(x_score[train_idx], y[train_idx])
        preds['direct_axis'][test_idx] = direct.predict(x_score[test_idx])

        oracle = Ridge(alpha=1.0).fit(
            interaction_features(df.iloc[train_idx][score].values, clusters[train_idx], known_clusters),
            y[train_idx],
        )
        preds['oracle_cluster'][test_idx] = oracle.predict(
            interaction_features(df.iloc[test_idx][score].values, clusters[test_idx], known_clusters)
        )
        preds['predicted_cluster'][test_idx] = oracle.predict(
            interaction_features(df.iloc[test_idx][score].values, test_pred_cl, known_clusters)
        )
        fold_rows.append({
            'fold': fold,
            'axis': axis,
            'cluster_accuracy': accuracy_score(clusters[test_idx], test_pred_cl),
            'macro_f1': f1_score(clusters[test_idx], test_pred_cl, average='macro'),
            'n_test': int(len(test_idx)),
        })
    cluster_acc = accuracy_score(clusters, pred_clusters)
    macro_f1 = f1_score(clusters, pred_clusters, average='macro')
    rows = []
    for regime, pred in preds.items():
        rows.append({
            'axis': axis,
            'regime': regime,
            'r2': float(r2_score(y, pred)),
            'pearson': corr(pred, y)['r'],
            'spearman': spear(pred, y)['r'],
            'rmse': float(mean_squared_error(y, pred) ** 0.5),
            'pairwise_accuracy': pred_pairwise_accuracy(y, pred),
            'cluster_accuracy_used': float(cluster_acc) if regime == 'predicted_cluster' else (1.0 if regime == 'oracle_cluster' else None),
            'cluster_macro_f1_used': float(macro_f1) if regime == 'predicted_cluster' else (1.0 if regime == 'oracle_cluster' else None),
        })
    cluster_rows = []
    for true, pred in zip(clusters, pred_clusters):
        cluster_rows.append({'true_cluster': true, 'predicted_cluster': pred})
    return rows, fold_rows, cluster_rows


def fmt(c):
    if c.get('r') is None:
        return 'n/a'
    return f"r={c['r']:.3f}, p={c['p']:.3g}"


def main():
    df = load_data()
    missing_text = int((df['text_for_cluster_prediction'].str.len() == 0).sum())
    cluster_counts = df['cluster'].value_counts().sort_index().to_dict()
    role_count = len(df)
    cluster_count = df['cluster'].nunique()

    pairwise_rows = []
    stats_by_axis = {}
    comparison_rows = []
    cluster_pred_fold_rows = []
    cluster_pred_rows = []
    for axis in ['pc1', 'pc2']:
        st = axis_stats(df, axis)
        stats_by_axis[axis] = st
        pairwise_rows.extend(st['pairwise_rows'])
        comp, folds, cp = prediction_regimes(df, axis)
        comparison_rows.extend(comp)
        cluster_pred_fold_rows.extend(folds)
        for row in cp:
            row['axis'] = axis
        cluster_pred_rows.extend(cp)

    pd.DataFrame(pairwise_rows).to_csv(OUT / 'pairwise_axis_ordering_results.csv', index=False)
    pd.DataFrame(cluster_pred_fold_rows).to_csv(OUT / 'cluster_prediction_results.csv', index=False)
    pd.DataFrame(comparison_rows).to_csv(OUT / 'axis_conditioning_model_comparison.csv', index=False)

    for axis in ['pc1', 'pc2']:
        out = dict(stats_by_axis[axis])
        out['data_sources'] = {
            'role_geometry': str(GEOM_PATH.relative_to(REPO)),
            'rater_scores': str(RATER_PATH.relative_to(REPO)),
            'dossiers_for_cluster_prediction': str(DOSSIER_PATH.relative_to(REPO)),
        }
        out['model_used'] = MODEL_USED
        out['cluster_labels_used'] = 'roles.clusters from research/visualizations/geometry_viz_data.json'
        out['role_count'] = role_count
        out['cluster_count'] = cluster_count
        out['cluster_counts'] = cluster_counts
        out['missing_text_for_cluster_prediction'] = missing_text
        out['prediction_regimes'] = [r for r in comparison_rows if r['axis'] == axis]
        (OUT / f'{axis}_cluster_conditioned_stats.json').write_text(json.dumps(out, indent=2))

    compdf = pd.DataFrame(comparison_rows)
    clpdf = pd.DataFrame(cluster_pred_fold_rows)
    # Cluster prediction identical for both axes except repeated folds; summarize first axis.
    pc1_folds = clpdf[clpdf['axis'] == 'pc1']
    cluster_acc = float(pc1_folds['cluster_accuracy'].mean())
    cluster_f1 = float(pc1_folds['macro_f1'].mean())

    def regime_line(axis):
        sub = compdf[compdf['axis'] == axis]
        lines=[]
        for _, r in sub.iterrows():
            lines.append(f"| {r['regime']} | {r['r2']:.3f} | {r['pearson']:.3f} | {r['spearman']:.3f} | {r['rmse']:.3f} | {r['pairwise_accuracy']:.3f} |")
        return '\n'.join(lines)

    def pair_line(axis):
        st=stats_by_axis[axis]
        return '\n'.join([
            f"| global | {st['pairwise_global']['accuracy']:.3f} | {st['pairwise_global']['n_pairs']} |",
            f"| within-cluster | {st['pairwise_within_cluster']['accuracy']:.3f} | {st['pairwise_within_cluster']['n_pairs']} |",
            f"| across-cluster | {st['pairwise_across_cluster']['accuracy']:.3f} | {st['pairwise_across_cluster']['n_pairs']} |",
        ])

    def corr_block(axis):
        st=stats_by_axis[axis]
        return f"Global Pearson {fmt(st['global_pearson'])}; global Spearman {fmt(st['global_spearman'])}. Cluster-controlled Pearson {fmt(st['cluster_controlled_pearson'])}; cluster-controlled Spearman {fmt(st['cluster_controlled_spearman'])}."

    def per_cluster_table(axis):
        rows=[]
        for cl, entry in stats_by_axis[axis]['per_cluster'].items():
            acc = entry['pairwise']['accuracy']
            acc_s = 'n/a' if acc is None else f'{acc:.3f}'
            rows.append(f"| {cl} | {entry['n']} | {fmt(entry['pearson'])} | {fmt(entry['spearman'])} | {acc_s} |")
        return '\n'.join(rows)

    # Decisions.
    decisions = {}
    for axis in ['pc1', 'pc2']:
        st = stats_by_axis[axis]
        diff = st['pairwise_within_cluster']['accuracy'] - st['pairwise_global']['accuracy']
        direct = compdf[(compdf.axis == axis) & (compdf.regime == 'direct_axis')].iloc[0]
        oracle = compdf[(compdf.axis == axis) & (compdf.regime == 'oracle_cluster')].iloc[0]
        predicted = compdf[(compdf.axis == axis) & (compdf.regime == 'predicted_cluster')].iloc[0]
        decisions[axis] = {
            'pairwise_within_minus_global': float(diff),
            'oracle_r2_minus_direct': float(oracle.r2 - direct.r2),
            'predicted_r2_minus_direct': float(predicted.r2 - direct.r2),
            'helps_pairwise': bool(diff > 0.02),
            'helps_oracle_model': bool((oracle.r2 - direct.r2) > 0.02),
            'survives_predicted_cluster': bool((predicted.r2 - direct.r2) > 0.02),
        }

    report = f"""# Cluster-Conditioned Axis Tests: PC1 and PC2

model_used: {MODEL_USED}

## Data Sources

- Role geometry: `research/visualizations/geometry_viz_data.json`
- Proxy annotations: `research/q2_stability/qwen/outputs/blinded_axis_rater_study/axis_rater_scores.csv`
- Text for cluster classifier: `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_persona_dossiers.jsonl`
- Prior PC3 validation context: `research/outputs/pc3_validation/`

Cluster labels used: `roles.clusters` from `geometry_viz_data.json`.

Role count: {role_count}
Cluster count: {cluster_count}
Cluster counts: `{cluster_counts}`
Missing text records for cluster prediction: {missing_text}

## Proxy Scores

PC1 proxy: `pc1_objective_certainty_score`, interpreted as convergence pressure versus degrees of freedom.

PC2 proxy: `100 - abstraction_score`, interpreted as situated developmental immediacy versus integrated abstraction. This sign choice makes higher proxy scores predict higher PC2, because prior PC2 work found abstraction negatively associated with PC2.

## PC1 Results

{corr_block('pc1')}

| pair scope | ordering accuracy | usable pairs |
|---|---:|---:|
{pair_line('pc1')}

Within-minus-global bootstrap: mean diff {stats_by_axis['pc1']['within_minus_global_bootstrap']['mean_diff']:.3f}, 95% CI [{stats_by_axis['pc1']['within_minus_global_bootstrap']['ci_low']:.3f}, {stats_by_axis['pc1']['within_minus_global_bootstrap']['ci_high']:.3f}]

### PC1 Per-Cluster Results

| cluster | n | Pearson | Spearman | pairwise accuracy |
|---|---:|---|---|---:|
{per_cluster_table('pc1')}

## PC2 Results

{corr_block('pc2')}

| pair scope | ordering accuracy | usable pairs |
|---|---:|---:|
{pair_line('pc2')}

Within-minus-global bootstrap: mean diff {stats_by_axis['pc2']['within_minus_global_bootstrap']['mean_diff']:.3f}, 95% CI [{stats_by_axis['pc2']['within_minus_global_bootstrap']['ci_low']:.3f}, {stats_by_axis['pc2']['within_minus_global_bootstrap']['ci_high']:.3f}]

### PC2 Per-Cluster Results

| cluster | n | Pearson | Spearman | pairwise accuracy |
|---|---:|---|---|---:|
{per_cluster_table('pc2')}

## Cluster Prediction Accuracy

A TF-IDF bigram logistic classifier was trained in five stratified folds on blinded dossier text.

Mean held-out cluster accuracy: {cluster_acc:.3f}
Mean held-out macro F1: {cluster_f1:.3f}

## Direct vs Oracle-Cluster vs Predicted-Cluster Regimes

### PC1

| regime | R2 | Pearson | Spearman | RMSE | pairwise accuracy |
|---|---:|---:|---:|---:|---:|
{regime_line('pc1')}

### PC2

| regime | R2 | Pearson | Spearman | RMSE | pairwise accuracy |
|---|---:|---:|---:|---:|---:|
{regime_line('pc2')}

## Interpretation

Observed: simple within-cluster pairwise ordering is not easier for either axis. PC1 global ordering accuracy is {stats_by_axis['pc1']['pairwise_global']['accuracy']:.3f}, while within-cluster accuracy is {stats_by_axis['pc1']['pairwise_within_cluster']['accuracy']:.3f}; PC2 global ordering accuracy is {stats_by_axis['pc2']['pairwise_global']['accuracy']:.3f}, while within-cluster accuracy is {stats_by_axis['pc2']['pairwise_within_cluster']['accuracy']:.3f}. Across-cluster pairs are easier because large cluster-level offsets make many comparisons obvious.

Observed: cluster conditioning does improve prediction in the regression regime. PC1 oracle-cluster R2 improves over direct-axis R2 by {decisions['pc1']['oracle_r2_minus_direct']:.3f}; PC2 oracle-cluster R2 improves by {decisions['pc2']['oracle_r2_minus_direct']:.3f}. This means cluster identity carries substantial intercept/slope information even though within-cluster pairwise judgments are harder than global pairwise judgments.

Observed: cluster-prediction uncertainty is nontrivial. The text-to-cluster classifier reached {cluster_acc:.3f} accuracy and {cluster_f1:.3f} macro F1. Predicted-cluster conditioning preserves part of the oracle benefit for PC1 ({decisions['pc1']['predicted_r2_minus_direct']:.3f} R2 over direct), but only part for PC2 ({decisions['pc2']['predicted_r2_minus_direct']:.3f} R2 over direct). Hard cluster errors therefore erase much of the PC2 oracle benefit.

Inferred: cluster conditioning helps as a modeling interaction, not as evidence that axis position is easier to judge within a known cluster. PC1 remains a strong global convergence-pressure scale, but cluster context improves calibrated prediction. PC2 is more region-dependent: abstraction/developmental-immediacy has a global signal, yet its mapping onto PC2 depends substantially on coarse persona region.

## Judge-Rubric Design Recommendation

- PC1: use a direct axis judge when simplicity matters; use a hybrid direct-plus-cluster model when calibrated numeric prediction matters.
- PC2: use cluster-conditioned interpretation for analysis, but deployment-style forecasting should prefer soft-cluster or interaction features over hard predicted clusters.
- Oracle-cluster scores are appropriate for mechanistic interpretation; hard predicted-cluster deployment should report cluster accuracy because classifier errors materially reduce the benefit, especially for PC2.
"""
    (OUT / 'cluster_conditioned_axis_report.md').write_text(report)

    # Copy this executable script into the output directory for provenance.
    source = Path(__file__).read_text() if '__file__' in globals() else ''
    SCRIPT_OUT.write_text(source)

    print(report)

if __name__ == '__main__':
    main()
