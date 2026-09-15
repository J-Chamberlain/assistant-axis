#!/usr/bin/env python3
"""Bootstrap and target-shuffle summaries for the locked validation rows."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'research/outputs/human_to_qwen_static_bridge'; PRIVATE=ROOT/'data_external/human_validation/sapa/derived/human_to_qwen_static_bridge_v1'
SEED=20260914; B=2000; D=1000

def macro(df, actual_col='actual_target_normal', pred_col='predicted_target_normal'):
    rs=[]
    for _,g in df.groupby('target_trait'):
        if len(g)>=100: rs.append(float(pearsonr(g[pred_col],g[actual_col]).statistic))
    return float(np.tanh(np.mean(np.arctanh(np.clip(rs,-.999999,.999999))))) if rs else float('nan')

def main():
    p=pd.read_parquet(PRIVATE/'heldout_predictions.parquet')
    rng=np.random.default_rng(SEED)
    respondents=p.anonymous_row.unique(); boot=[]
    groups={int(i):g for i,g in p.groupby('anonymous_row',sort=False)}
    for _ in range(B):
        chosen=rng.choice(respondents,size=len(respondents),replace=True)
        boot.append(macro(pd.concat([groups[int(i)] for i in chosen],ignore_index=True)))
    boot=np.asarray(boot); observed=macro(p)
    null=[]
    for _ in range(D):
        q=p.copy()
        for t,gidx in q.groupby('target_trait').groups.items(): q.loc[gidx,'actual_target_normal']=rng.permutation(q.loc[gidx,'actual_target_normal'].to_numpy())
        null.append(macro(q))
    null=np.asarray(null)
    summary={'observed_macro':observed,'bootstrap_draws':B,'bootstrap_seed':SEED,'bootstrap_ci95':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],'target_shuffle_draws':D,'target_shuffle_seed':SEED,'target_shuffle_empirical_p':float((np.sum(null>=observed)+1)/(D+1)),'target_shuffle_exceedances':int(np.sum(null>=observed))}
    (OUT/'uncertainty_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    null_rows=[{'null_family':'human_target_shuffle','draws':D,'seed':SEED,'observed_macro':observed,'null_mean':float(null.mean()),'null_sd':float(null.std(ddof=1)),'null_q025':float(np.quantile(null,.025)),'null_q975':float(np.quantile(null,.975)),'exceedances':int(np.sum(null>=observed)),'empirical_p':summary['target_shuffle_empirical_p'],'status':'COMPLETE'}]
    null_rows += [
      {'null_family':'bridge_label_permutation','draws':0,'seed':20260915,'observed_macro':observed,'status':'NOT_RUN_CPU_BUDGET','reason':'requires refitting location and decoder mappings per draw; no outcome-based shortcut used'},
      {'null_family':'model_joint_structure_destruction','draws':0,'seed':20260916,'observed_macro':observed,'status':'NOT_RUN_CPU_BUDGET','reason':'requires model-side refits per draw; no outcome-based shortcut used'}]
    pd.DataFrame(null_rows).to_csv(OUT/'null_summary.csv',index=False)
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
