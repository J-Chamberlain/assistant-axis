"""CPU-only corrected AA22 transport versus frozen AA21; no human refit or inference."""
from pathlib import Path
import base64, hashlib, json, subprocess
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'research/outputs'
inputs=set()
def csv(p):
    p=OUT/p;inputs.add(p);return pd.read_csv(p)
def js(p):
    p=OUT/p;inputs.add(p);return json.loads(p.read_text())
def angle(a,b):
    return float(np.degrees(np.arccos(np.clip(np.dot(a,b)/np.linalg.norm(a)/np.linalg.norm(b),-1,1))))
def main():
    w=csv('aa26_sapa_profile_information_gain/dependency_repair/AA22/trait_weight_sensitivity.csv').set_index('trait')
    oldw=csv('aa22_direct_trait_hifwb_bridge/trait_weight_sensitivity.csv').set_index('trait').loc[w.index]
    baseline=csv('aa21_bigfive_hifwb_persona_projection/persona_bigfive_hifwb_projection.csv')
    baseline=baseline[(baseline.human_fit=='full_overlap_primary')&(baseline.construction=='external_taxonomy_expanded')]
    old=csv('aa22_direct_trait_hifwb_bridge/persona_direct_trait_hifwb_projection.csv')
    coeff=csv('aa21_bigfive_hifwb_persona_projection/human_bigfive_hifwb_coefficients.csv')
    coeff=coeff[coeff.human_fit=='full_overlap_primary'].set_index('domain').standardized_coefficient
    bigscores=csv('externally_anchored_big_five/big_five_role_scores.csv')
    manifest=js('externally_anchored_big_five/big_five_domain_directions_manifest.json')['directions']
    traitpcs=csv('three_model_trait_pca/trait_pc_scores_all.csv')
    coords=js('extended_persona_pca/viewer_data.json')['models']
    paths={'qwen':'trait_persona_prediction/persona_trait_similarity_matrix.csv','llama':'multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv','gemma':'multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv'}
    summary=[];frames=[];planes=[];directions=[];checks={}
    for model,path in paths.items():
        m=csv(path).set_index('persona'); assert m.shape==(275,240) and m.index.is_unique and np.isfinite(m).all().all()
        X=m[w.index]; z=(X-X.mean())/X.std(ddof=1)
        weights=w.weight_full_sample.to_numpy(); a=weights/np.abs(weights).sum()
        direct=z.to_numpy()@a
        b=baseline[baseline.model==model].set_index('persona').loc[m.index]
        g=pd.DataFrame({'model':model,'persona':m.index,'bigfive_score':b.hifwb_associated_score_sd.to_numpy(),'direct_score':direct})
        for name in ['bigfive','direct']:
            g[name+'_rank']=g[name+'_score'].rank(ascending=False,method='average')
            g[name+'_percentile']=g[name+'_score'].rank(pct=True,method='average')*100
        g['rank_improvement_direct']=g.bigfive_rank-g.direct_rank
        historical=old[old.model.str.lower()==model].set_index('persona').loc[m.index].direct_trait_hifwb_score.to_numpy()
        oldcalc=z.to_numpy()@(oldw.weight_full_sample.to_numpy()/oldw.weight_full_sample.abs().sum())
        checks[model+'_old_transport_reproduction_max_error']=float(np.max(abs(oldcalc-historical)))
        assert np.max(abs(oldcalc-historical))<1e-10
        summary.append(dict(model=model,pearson_r=g.bigfive_score.corr(g.direct_score),spearman_rho=spearmanr(g.bigfive_score,g.direct_score).statistic,top10_overlap=len(set(g.nsmallest(10,'bigfive_rank').persona)&set(g.nsmallest(10,'direct_rank').persona)),bottom10_overlap=len(set(g.nlargest(10,'bigfive_rank').persona)&set(g.nlargest(10,'direct_rank').persona)),median_absolute_rank_change=g.rank_improvement_direct.abs().median(),maximum_absolute_rank_change=g.rank_improvement_direct.abs().max(),corrected_vs_old_score_max_change=float(np.max(abs(direct-historical)))))
        # Reconstruct all 240 raw trait vectors from the complete 239-component trait PCA.
        npz=OUT/f'three_model_trait_pca/{model}_trait_pca_directions.npz';inputs.add(npz)
        bundle=np.load(npz); ts=traitpcs[traitpcs.model==model].set_index('trait').loc[m.columns]
        T=ts[[f'trait_pc{i}' for i in range(1,240)]].to_numpy()@bundle['directions'].astype(float)+bundle['mean'].astype(float)
        T=T/np.linalg.norm(T,axis=1,keepdims=True); trait_idx={t:i for i,t in enumerate(m.columns)}
        d=(a/X.std(ddof=1).to_numpy())@T[[trait_idx[t] for t in w.index]]
        bfvec=np.zeros(T.shape[1]); ub=np.zeros(len(m)); base_repro=np.zeros(len(m)); domain_errors=[]
        for domain,c in coeff.items():
            key='neuroticism' if domain=='emotional_stability' else domain
            sign=-1 if domain=='emotional_stability' else 1
            item=manifest[f'{model}__external_taxonomy_expanded__{key}']
            vec=np.frombuffer(base64.b64decode(item['vector_base64']),dtype='<f4').astype(float)
            pos=item['positive_traits']; neg=item['negative_traits']
            rec=(T[[trait_idx[t] for t in pos]].mean(0) if pos else np.zeros(T.shape[1]))-(T[[trait_idx[t] for t in neg]].mean(0) if neg else np.zeros(T.shape[1]))
            rec/=np.linalg.norm(rec);domain_errors.append(np.max(abs(rec-vec)))
            q=bigscores[(bigscores.model==model)&(bigscores.construction=='external_taxonomy_expanded')&(bigscores.domain==key)].set_index('persona').loc[m.index].raw_projection_score.to_numpy()
            bfvec+=c*sign*vec/q.std(ddof=1);ub+=c*sign*q/q.std(ddof=1)
            base_repro+=c*sign*(q-q.mean())/q.std(ddof=1)
        checks[model+'_trait_reconstruction_domain_max_error']=float(max(domain_errors));assert max(domain_errors)<2e-6
        checks[model+'_bigfive_centered_reproduction_error']=float(np.max(abs((base_repro-base_repro.mean())-(g.bigfive_score-g.bigfive_score.mean()))));assert checks[model+'_bigfive_centered_reproduction_error']<1e-10
        ud=X.to_numpy()@(a/X.std(ddof=1).to_numpy())
        # For score s(h)=b dot h/||h|| + offset, gradient direction is b-u(u dot b).
        # Pairwise local gradient angle requires only b,d and u dot b,u dot d, not full role tensors.
        tangent_cos=(bfvec@d-ub*ud)/np.sqrt((bfvec@bfvec-ub**2)*(d@d-ud**2))
        assert np.isfinite(tangent_cos).all() and np.max(abs(tangent_cos))<1+1e-6
        g['full_space_local_gradient_angle_degrees']=np.degrees(np.arccos(np.clip(tangent_cos,-1,1)))
        directions.append(dict(model=model,readout_vector_angle_degrees=angle(bfvec,d),local_gradient_angle_min=g.full_space_local_gradient_angle_degrees.min(),local_gradient_angle_median=g.full_space_local_gradient_angle_degrees.median(),local_gradient_angle_max=g.full_space_local_gradient_angle_degrees.max()))
        pc=pd.DataFrame({p['persona']:p['coordinates'] for p in coords[model]['points']}).T.loc[m.index].to_numpy()
        for k in [3,5]:
            for metric in ['raw_PC_units','standardized_PC_units']:
                P=pc[:,:k].copy()
                if metric=='standardized_PC_units':P=(P-P.mean(0))/P.std(0,ddof=1)
                fits=[];row=dict(model=model,dimensions=k,metric=metric)
                for name in ['bigfive','direct']:
                    y=g[name+'_score'].to_numpy();fit=LinearRegression().fit(P,y);fits.append(fit.coef_)
                    row[name+'_in_sample_r2']=r2_score(y,fit.predict(P))
                    row[name+'_fivefold_r2']=r2_score(y,cross_val_predict(LinearRegression(),P,y,cv=KFold(5,shuffle=True,random_state=20260921)))
                    for i,val in enumerate(fit.coef_/np.linalg.norm(fit.coef_)):row[f'{name}_unit_direction_PC{i+1}']=val
                row['fitted_gradient_angle_degrees']=angle(*fits);planes.append(row)
        frames.append(g)
    scores=pd.concat(frames,ignore_index=True);s=pd.DataFrame(summary);dr=pd.DataFrame(directions);pl=pd.DataFrame(planes)
    scores.to_csv(HERE/'persona_comparison.csv',index=False);s.to_csv(HERE/'ranking_agreement.csv',index=False);dr.to_csv(HERE/'activation_direction_agreement.csv',index=False);pl.to_csv(HERE/'pc_plane_diagnostics.csv',index=False)
    checks['corrected_vs_old_full_sample_weight_max_change']=float(np.max(abs(w.weight_full_sample-oldw.weight_full_sample)))
    checks['all_models_personas']=len(scores)==825
    (HERE/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
    (HERE/'source_manifest.json').write_text(json.dumps({'source_commit':'6de44e52d064c929f43740f2237e8e5be9748bca','method':'Frozen AA22 transport with corrected full-sample weights; AA21 primary expanded baseline','inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)},'model_identity':'unknown','model_inference':False,'paid_compute':False,'human_data_refit':False},indent=2)+'\n')
    print(s.to_string(index=False));print(dr.to_string(index=False));print(pl[['model','dimensions','metric','fitted_gradient_angle_degrees','bigfive_fivefold_r2','direct_fivefold_r2']].to_string(index=False));print(json.dumps(checks,indent=2))
    print(scores[scores.model=='qwen'].sort_values('rank_improvement_direct',key=abs,ascending=False).head(8).to_string(index=False))
if __name__=='__main__':main()
