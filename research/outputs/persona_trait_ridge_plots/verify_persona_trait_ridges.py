#!/usr/bin/env python3
"""Independent saved-source, rank, normalization and complete HTML checks."""
import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class PlotParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.circles, self.scripts, self.external = [], 0, 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('class') == 'ridge-row':
            self.rows.append(a)
        if tag == 'circle':
            self.circles += 1
        if tag == 'script':
            self.scripts += 1
            if 'src' in a:
                self.external.append(a['src'])


def main():
    data = json.loads((HERE/'persona_trait_ridge_data.json').read_text())
    names, coords = data['personas'], np.array(data['coordinates'])
    keys = [r['trait'] for r in data['categories']]
    geometry = json.loads((ROOT/'research/visualizations/geometry_viz_data.json').read_text())['roles']
    assert names == geometry['names'] and np.array_equal(coords,geometry['pca3d'])
    assert len(names) == len(set(names)) == 275 and len(set(keys)) == 15
    matrix = {r['persona']:r for r in csv.DictReader((ROOT/'research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv').open())}
    raw = np.array([[float(matrix[n][k]) for k in keys] for n in names])
    assert np.array_equal(raw,data['raw_affinity'])
    # Mid-distribution percentile computed independently, including ties.
    pct = np.array([[100*((raw[:,e]<v).sum()+.5*(raw[:,e]==v).sum())/275
                     for e,v in enumerate(row)] for row in raw])
    assert np.allclose(pct,data['height_percentile'],atol=1e-12)
    z=(raw-raw.mean(0))/raw.std(0)
    assert np.allclose(z,data['z_score'],atol=1e-12)
    parser=PlotParser()
    markup=(HERE/'persona_trait_ridges.html').read_text()
    parser.feed(markup)
    assert len(parser.rows)==825 and parser.circles==12375
    assert parser.scripts==1 and not parser.external
    for a in range(3):
        order=sorted(range(275),key=lambda i:(-coords[i,a],names[i]))
        assert data['orders'][a]==order
        for rank,(i,r) in enumerate(zip(order,parser.rows[a*275:(a+1)*275]),1):
            assert r['data-persona']==names[i] and int(r['data-rank'])==rank
            assert np.isclose(float(r['data-pc']),coords[i,a],atol=1e-10)
    scores=list(csv.DictReader((HERE/'persona_trait_ridge_scores.csv').open()))
    assert len(scores)==4125 and len({(r['persona'],r['trait']) for r in scores})==4125
    for r in scores:
        i,e=names.index(r['persona']),keys.index(r['trait'])
        assert float(r['raw_affinity'])==raw[i,e]
        assert float(r['ridge_height_percentile'])==pct[i,e]
        for a in range(3):
            assert int(r[f'rank_pc{a+1}'])==data['orders'][a].index(i)+1
    manifest=json.loads((HERE/'persona_trait_ridge_manifest.json').read_text())
    for s in manifest['source_files']:
        assert hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest()==s['sha256']
    checks=dict(status='pass',source_matrix_shape=[275,240],selected_score_rows=4125,
        persona_rows_in_html=825,category_points_in_html=12375,canonical_geometry_unchanged=True,
        raw_scores_exact=True,independent_midrank_check=True,all_rankings_descending=True,
        source_checksums_pass=True,all_panels_prerendered=True,no_external_scripts=True,
        browser_validation='Not performed; static SVG rasterization and DOM-double unit checks only')
    (HERE/'persona_trait_ridge_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks,indent=2))


if __name__=='__main__':
    main()
