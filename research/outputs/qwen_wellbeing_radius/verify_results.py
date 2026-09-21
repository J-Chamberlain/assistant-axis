"""Validate saved endpoint constraints, cross-objective evaluation, and alternative separation."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
def angle(a,b):return float(np.degrees(np.arccos(np.clip(a@b/np.linalg.norm(a)/np.linalg.norm(b),-1,1))))
d=pd.read_csv(HERE/'radius_candidates.csv');p=pd.read_csv(HERE/'peak_search_diagnostics.csv');v=json.load(open(HERE/'verification.json'))
assert len(d)==11550 and len(p)==3300
assert not d.duplicated(['persona','dimensions','radius','candidate']).any()
assert np.isfinite(d.select_dtypes(include='number').to_numpy()).all()
assert (p.optimized_gain>=p.sample_best_gain-1e-7).all()
assert d[['bigfive_gain_fraction','direct_gain_fraction']].max().max()<1+1e-5
mins=[]
for key,g in d.groupby(['persona','dimensions','radius']):
    assert len(g)==7
    g=g.set_index('candidate')
    for bridge in ['bigfive','direct']:
        assert np.allclose(g['delta_'+bridge],g[bridge+'_end']-g[bridge+'_start'],atol=1e-12)
        assert np.allclose(g[bridge+'_gain_fraction'],g['delta_'+bridge]/g.loc[bridge+'_optimum','delta_'+bridge],atol=1e-10)
        dirs=g.loc[[bridge+'_optimum',bridge+'_alternative_1',bridge+'_alternative_2'],[f'unit_PC{i}' for i in range(1,6)]].to_numpy()
        for i in range(3):
            for j in range(i):mins.append(angle(dirs[i],dirs[j]))
        # The compromise must not underperform the better of the two optima on its maximin objective.
        fractions=g[['bigfive_gain_fraction','direct_gain_fraction']].min(axis=1)
        assert fractions['compromise']>=max(fractions['bigfive_optimum'],fractions['direct_optimum'])-1e-6
assert min(mins)>45-1e-4
v.update(saved_rows_finite_and_unique=True,all_optimized_scores_beat_sampled_starts=True,all_candidate_gains_bounded_by_individual_optima=True,minimum_alternative_pairwise_angle_degrees=min(mins),compromise_beats_both_single_objective_choices_on_maximin=True)
(HERE/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v,indent=2))
