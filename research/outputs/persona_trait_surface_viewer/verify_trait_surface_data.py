#!/usr/bin/env python3
"""Independent checks of aggregation, source hashes and bounded/masked meshes."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
d=json.loads((HERE/'persona_trait_surface_data.json').read_text())
r=json.loads((ROOT/'research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json').read_text())
assert [x['name'] for x in d['roles']]==r['personas']
assert [x['pcs'] for x in d['roles']]==r['coordinates']
assert len(d['roles'])==275 and len(d['categories'])==5
for c in d['categories']:
    indices=[i for i,t in enumerate(r['categories']) if t['group']==c['label']]
    assert len(indices)==3
    source=np.asarray(r['height_percentile'])[:,indices]
    assert np.array_equal(np.asarray(c['values']),source.mean(1))
    assert abs(np.mean(c['values'])-50)<1e-12
    for m,j in zip(c['members'],indices):
        assert m['key']==r['categories'][j]['trait']
        assert np.array_equal(m['percentile'],np.asarray(r['height_percentile'])[:,j])
        assert np.array_equal(m['raw'],np.asarray(r['raw_affinity'])[:,j])
assert len(d['views'])==3
old=json.loads((ROOT/'research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_data.json').read_text())
for key,v in d['views'].items():
    assert len(v['levels'])==3
    assert v['x']==old['views'][key]['x'] and v['y']==old['views'][key]['y']
    for level in v['levels']:
        assert len(level['grids'])==5
        for i,grid in enumerate(level['grids']):
            assert len(grid)==61 and all(len(row)==61 for row in grid)
            array=np.array([[np.nan if x is None else x for x in row] for row in grid])
            baseline=old['views'][key]['levels'][0]['grids'][0]
            assert np.array_equal(np.isnan(array),np.array([[x is None for x in row] for row in baseline]))
            assert np.nanmin(array)>=0 and np.nanmax(array)<=100
            f=np.array(level['fitted_nodes'][i]);assert len(f)==275 and np.isfinite(f).all()
            rmse=np.sqrt(np.mean((f-np.array(d['categories'][i]['values']))**2))
            assert abs(rmse-level['fit_rmse'][i])<1e-10
rows=list(csv.DictReader((HERE/'persona_trait_group_scores.csv').open()))
assert len(rows)==len({(x['persona'],x['group']) for x in rows})==1375
for row in rows:
    assert abs(float(row['group_mean_trait_percentile'])-sum(float(row[f'percentile_{i}']) for i in [1,2,3])/3)<1e-12
manifest=json.loads((HERE/'trait_surface_manifest.json').read_text())
for f in manifest['sources']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
html=(HERE/'persona_trait_surface_viewer.html').read_text()
for token in ['__BOOTSTRAP_JS__','__PLOTLY_LIBRARY__','__VIEWER_DATA__','__CAMERA_JS__','__VIEWER_JS__']:
    assert token not in html
assert '<script src=' not in html and '__traitViewer' in html
result=dict(status='pass',personas=275,groups=5,rows=1375,surface_variants=45,
    exact_geometry=True,exact_member_scores=True,equal_weight_mean=True,population_group_mean=50,
    all_meshes_bounded=True,same_support_masks_as_emotion_viewer=True,source_hashes=True,
    self_contained_html=True,no_pca_refit=True,new_activations=False)
(HERE/'trait_surface_data_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
