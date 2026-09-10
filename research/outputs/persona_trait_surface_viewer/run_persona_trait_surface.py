#!/usr/bin/env python3
"""Build a self-contained 3D viewer of five existing editorial trait groups."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

import numpy as np
import plotly
from plotly.offline import get_plotlyjs
from scipy.interpolate import RBFInterpolator
from scipy.spatial import Delaunay, cKDTree

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RIDGES=ROOT/'research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json'
GEOMETRY=ROOT/'research/visualizations/geometry_viz_data.json'
SMOOTHING=[('Detail',.003),('Balanced',.03),('Gentle',.3)]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(name,data):
    (HERE/name).write_text(json.dumps(data,allow_nan=False,indent=2)+'\n')


def save_csv(name,rows):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def load_groups():
    d=json.loads(RIDGES.read_text())
    g=json.loads(GEOMETRY.read_text())['roles']
    assert d['personas']==g['names'] and d['coordinates']==g['pca3d']
    assert len(d['personas'])==len(set(d['personas']))==275
    assert len(d['categories'])==15
    pct,z,raw=[np.asarray(d[k]) for k in ['height_percentile','z_score','raw_affinity']]
    assert pct.shape==z.shape==raw.shape==(275,15)
    assert np.isfinite(pct).all() and np.all((pct>=0)&(pct<=100))
    groups=[];rows=[]
    for label in dict.fromkeys(c['group'] for c in d['categories']):
        indices=[i for i,c in enumerate(d['categories']) if c['group']==label]
        assert len(indices)==3
        members=[dict(key=d['categories'][j]['trait'],label=d['categories'][j]['trait'].capitalize(),
                      percentile=pct[:,j].tolist(),raw=raw[:,j].tolist(),z=z[:,j].tolist()) for j in indices]
        mean=pct[:,indices].mean(1)
        assert abs(mean.mean()-50)<1e-10
        groups.append(dict(key=label.lower(),label=label,values=mean.tolist(),
                           mean_z=z[:,indices].mean(1).tolist(),members=members))
        for i,name in enumerate(d['personas']):
            r=dict(persona=name,group=label,group_mean_trait_percentile=float(mean[i]),
                   group_mean_trait_z=float(z[i,indices].mean()),pc1=d['coordinates'][i][0],
                   pc2=d['coordinates'][i][1],pc3=d['coordinates'][i][2])
            for m,j in enumerate(indices,1):
                r.update({f'trait_{m}':d['categories'][j]['trait'],f'percentile_{m}':float(pct[i,j]),
                          f'raw_cosine_{m}':float(raw[i,j]),f'z_{m}':float(z[i,j])})
            rows.append(r)
    assert len(groups)==5 and len(rows)==1375
    roles=[dict(name=n,pcs=pc) for n,pc in zip(d['personas'],d['coordinates'])]
    return roles,groups,rows


def make_meshes(roles,groups):
    coords=np.array([r['pcs'] for r in roles]);scores=np.array([g['values'] for g in groups]).T
    views={};diagnostics=[]
    for axes in itertools.combinations(range(3),2):
        xy=coords[:,axes];center=xy.mean(0);scale=float(np.sqrt(np.mean(np.var(xy,axis=0))))
        points=(xy-center)/scale
        unique,inverse=np.unique(points,axis=0,return_inverse=True)
        targets=np.stack([scores[inverse==i].mean(0) for i in range(len(unique))])
        tree=cKDTree(unique);dist,_=tree.query(unique,k=6);radius=float(np.quantile(dist[:,-1],.9))
        x=np.linspace(xy[:,0].min(),xy[:,0].max(),61);y=np.linspace(xy[:,1].min(),xy[:,1].max(),61)
        xx,yy=np.meshgrid(x,y);grid=(np.column_stack([xx.ravel(),yy.ravel()])-center)/scale
        sixth,_=tree.query(grid,k=6)
        supported=((Delaunay(unique).find_simplex(grid)>=0)&(sixth[:,-1]<=radius)).reshape(61,61)
        node_basis=np.column_stack([np.ones(len(points)),points])
        grid_basis=np.column_stack([np.ones(len(grid)),grid])
        flat_grid_arrays=[];flat_plane=[]
        for c in range(len(groups)):
            coefficients=np.linalg.lstsq(node_basis,scores[:,c],rcond=None)[0]
            flat_nodes_raw=node_basis@coefficients
            flat_grid_raw=(grid_basis@coefficients).reshape(61,61)
            node_sst=float(np.sum((scores[:,c]-scores[:,c].mean())**2))
            node_sse=float(np.sum((scores[:,c]-flat_nodes_raw)**2))
            node_r2=None if node_sst<1e-12 else float(1-node_sse/node_sst)
            flat_grid_arrays.append(np.clip(flat_grid_raw,0,100))
            flat_plane.append(dict(coefficients=coefficients.tolist(),
                                   node_rmse=float(np.sqrt(np.mean((scores[:,c]-flat_nodes_raw)**2))),
                                   node_r2=node_r2))
        flat_grids=[[[round(float(v),6) if ok else None for v,ok in zip(row,supported_row)]
                     for row,supported_row in zip(flat_grid,supported)]
                    for flat_grid in flat_grid_arrays]
        levels=[]
        for label,smoothing in SMOOTHING:
            fit=RBFInterpolator(unique,targets,kernel='thin_plate_spline',smoothing=smoothing,degree=1)
            original=fit(grid).reshape(61,61,5);fitted_original=fit(points)
            assert np.isfinite(original).all() and np.isfinite(fitted_original).all()
            values=np.clip(original,0,100);fitted=np.clip(fitted_original,0,100)
            rmse=np.sqrt(np.mean((fitted-scores)**2,axis=0))
            grids=[];flat_adherence=[]
            for c in range(len(groups)):
                grids.append([[round(float(v),6) if ok else None for v,ok in zip(row,mask)]
                              for row,mask in zip(values[:,:,c],supported)])
                displayed=original[:,:,c][supported]
                rolling=values[:,:,c][supported]
                flat=flat_grid_arrays[c][supported]
                flat_sse=float(np.sum((rolling-flat)**2))
                rolling_sst=float(np.sum((rolling-rolling.mean())**2))
                flat_r2=None if rolling_sst<1e-12 else float(1-flat_sse/rolling_sst)
                flat_score=None if flat_r2 is None else float(np.clip(100*flat_r2,0,100))
                flat_adherence.append(dict(fabric_flat_rmse=float(np.sqrt(np.mean((rolling-flat)**2))),
                                           fabric_flat_r2=flat_r2,
                                           fabric_flat_score=flat_score))
                diagnostics.append(dict(x_axis=axes[0]+1,y_axis=axes[1]+1,group=groups[c]['label'],
                    smoothing_label=label,smoothing=smoothing,fit_rmse_percentile_points=float(rmse[c]),
                    support_fraction=float(supported.mean()),supported_cells=int(supported.sum()),
                    clipped_supported_cells=int(((displayed<0)|(displayed>100)).sum()),
                    fitted_nodes_clipped=int(((fitted_original[:,c]<0)|(fitted_original[:,c]>100)).sum()),
                    unclipped_supported_min=float(displayed.min()),unclipped_supported_max=float(displayed.max()),
                    maximum_node_fabric_gap=float(np.max(np.abs(fitted[:,c]-scores[:,c]))),
                    flat_plane_node_rmse=flat_plane[c]['node_rmse'],flat_plane_node_r2=flat_plane[c]['node_r2'],
                    fabric_flat_rmse=flat_adherence[-1]['fabric_flat_rmse'],fabric_flat_r2=flat_r2,
                    fabric_flat_score=flat_score))

            levels.append(dict(label=label,smoothing=smoothing,grids=grids,
                               fitted_nodes=fitted.T.tolist(),fit_rmse=rmse.tolist(),
                               flat_adherence=flat_adherence))
        views[f'{axes[0]}_{axes[1]}']=dict(axes=list(axes),x=x.tolist(),y=y.tolist(),levels=levels,
            fit_center=center.tolist(),fit_common_scale=scale,support_sixth_neighbor_radius=radius,
            supported_grid_fraction=float(supported.mean()),flat_grids=flat_grids,flat_plane=flat_plane)
    return views,diagnostics


def build_html(data):
    text=(HERE/'viewer_template.html').read_text()
    replacements={'__BOOTSTRAP_JS__':(HERE/'viewer_bootstrap.js').read_text(),
        '__PLOTLY_LIBRARY__':get_plotlyjs(),'__VIEWER_DATA__':json.dumps(data,separators=(',',':'),allow_nan=False).replace('</','<\\/'),
        '__CAMERA_JS__':(HERE/'camera_controls.js').read_text(),'__VIEWER_JS__':(HERE/'viewer.js').read_text()}
    for token,value in replacements.items():
        assert text.count(token)==1,token
        text=text.replace(token,value)
    assert not any(token in text for token in replacements)
    (HERE/'persona_trait_surface_viewer.html').write_text(text)


def inventory():
    files=sorted(p for p in HERE.iterdir() if p.is_file() and p.name!='artifact_inventory.csv')
    save_csv('artifact_inventory.csv',[dict(path=str(p.relative_to(ROOT)),size_bytes=p.stat().st_size,sha256=digest(p),
        raw_github_url='https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/'+str(p.relative_to(ROOT))) for p in files])


def main():
    roles,groups,rows=load_groups();views,diagnostics=make_meshes(roles,groups)
    data=dict(roles=roles,categories=groups,views=views,height_range=[0,100],
        aggregation='Equal-weight mean of three within-trait midrank percentiles from the ridge plots',
        caveat='Editorial same-space trait-cosine summaries, not independently validated factors or probabilities')
    save_csv('persona_trait_group_scores.csv',rows);save_csv('trait_surface_fit_diagnostics.csv',diagnostics)
    save_json('persona_trait_surface_data.json',data);build_html(data)
    source_paths=[RIDGES,GEOMETRY,ROOT/'research/outputs/persona_trait_ridge_plots/trait_category_order.csv',
        ROOT/'research/outputs/persona_trait_ridge_plots/persona_trait_ridge_manifest.json',
        ROOT/'research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md',
        ROOT/'research/outputs/persona_emotion_surface_viewer/run_persona_emotion_surface_viewer.py',
        HERE/'run_persona_trait_surface.py',HERE/'viewer.js',HERE/'camera_controls.js',HERE/'viewer_template.html',
        HERE/'viewer_bootstrap.js',HERE/'trait_surface_methodology.md']
    save_json('trait_surface_manifest.json',dict(generated_utc=datetime.now(timezone.utc).isoformat(),
        base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
        activation_model='Qwen/Qwen3-32B',author='Codex; exact runtime identifier not recorded',
        gpu_used=False,api_calls=0,new_activations=False,pca_refit=False,plotly_python_version=plotly.__version__,
        personas=275,groups=5,member_traits=15,group_rows=1375,ordered_axis_views=6,
        aggregation=data['aggregation'],grid_size=61,smoothing=SMOOTHING,
        height_range=[0,100],color_range=[0,100],bounded_fabric='Clip fitted surface only to 0-100; preserve exact group nodes',
        flat_plane_fit='Least-squares plane over intercept and normalized selected-PC coordinates; same support mask as rolling fabric',
        flat_adherence='Descriptive R2 of the flat plane as an approximation to each displayed rolling fabric; user score clips 100*R2 to 0-100',
        fit_diagnostics='In-sample descriptive errors; not held-out validation',
        sources=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p)) for p in source_paths]))
    print(json.dumps(dict(personas=275,groups=[g['label'] for g in groups],rows=1375,mesh_variants=45,
        clipped_cells=sum(r['clipped_supported_cells'] for r in diagnostics)),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inventory-only',action='store_true');p.add_argument('--html-only',action='store_true');args=p.parse_args()
    if args.html_only:
        build_html(json.loads((HERE/'persona_trait_surface_data.json').read_text()))
    elif not args.inventory_only:
        main()
    inventory()
