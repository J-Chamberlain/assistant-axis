"""Independent exported-data, ordering and pre-rendered-HTML checks."""
import csv
from html.parser import HTMLParser
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.circles, self.external = [], 0, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('class') == 'ridge-row':
            self.rows.append(attrs)
        if tag == 'circle':
            self.circles += 1
        if tag in ('script', 'img', 'link') and ('src' in attrs or 'href' in attrs):
            self.external.append(attrs)


data = json.loads((HERE/'persona_emotion_ridge_data.json').read_text())
geometry = json.loads((ROOT/'research/visualizations/geometry_viz_data.json').read_text())['roles']
assert data['personas'] == geometry['names']
assert data['coordinates'] == geometry['pca3d']
raw, z, pct = [np.asarray(data[k]) for k in ['raw_affinity', 'z_score', 'height_percentile']]
assert raw.shape == z.shape == pct.shape == (275, 10)
assert np.allclose(z, (raw-raw.mean(0))/raw.std(0), atol=1e-12)
for e in range(10):
    assert np.allclose(pct[:,e], 100*(rankdata(raw[:,e])-.5)/275, atol=1e-12)
values = [e['valence_raw'] for e in data['categories']]
assert values == sorted(values) and values[4] < 0 < values[5]
source = (HERE/'persona_emotion_ridges.html').read_text()
p = Inspect(); p.feed(source)
assert len(p.rows) == 825 and p.circles == 8250 and not p.external
assert '__PLOTLY_LIBRARY__' not in source and '__VIEWER_DATA__' not in source
for a in range(3):
    expected = sorted(range(275), key=lambda i: (-data['coordinates'][i][a], data['personas'][i]))
    assert expected == data['orders'][a]
    rows = p.rows[a*275:(a+1)*275]
    assert [r['data-persona'] for r in rows] == [data['personas'][i] for i in expected]
    assert [int(r['data-rank']) for r in rows] == list(range(1,276))
    svg = ET.parse(HERE/f'persona_emotion_ridges_pc{a+1}.svg')
    assert len(svg.findall('.//{http://www.w3.org/2000/svg}circle')) == 2750
exported = list(csv.DictReader((HERE/'persona_emotion_ridge_scores.csv').open()))
assert len(exported) == len({(r['persona'],r['emotion']) for r in exported}) == 2750
for r in exported:
    i = data['personas'].index(r['persona'])
    e = next(e for e,c in enumerate(data['categories']) if c['key'] == r['emotion'])
    assert float(r['ridge_height_percentile']) == pct[i,e]
    assert float(r['raw_affinity']) == raw[i,e]
print('PASS: exact source geometry; 2,750 unique scores; 825 ranked ridges; 8,250 exact markers; normalization; all 3 full SVGs; no external resources or build placeholders.')
