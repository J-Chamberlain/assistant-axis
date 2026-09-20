#!/usr/bin/env python3
"""Render the corrected human-only report and static performance figure."""
from aa26_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
s=json.loads((OUT/'information_gain_summary.json').read_text());g=json.loads((OUT/'repair/target_validity_gate.json').read_text())
r=pd.read_csv(OUT/'candidate_dimension_ranking.csv');c=pd.read_csv(OUT/'minimal_set_curve.csv');m=pd.read_csv(OUT/'profile_reconstruction_comparison.csv').set_index('analysis');sec=pd.read_csv(OUT/'secondary_outcome_comparison.csv');sel=pd.read_csv(OUT/'selected_question_or_construct_set.csv');tol=pd.read_csv(OUT/'minimal_set_tolerance_sensitivity.csv');k4=c[c.k==4].iloc[0];k5=c[c.k==5].iloc[0]
def table(df):
    # No optional tabulate dependency.
    return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(str(x) for x in row)+' |' for row in df.itertuples(index=False,name=None))+'\n'
rows=[]
for x in r[r.rank_distinct_final<=5].itertuples():
    rows.append(dict(Rank=int(x.rank_distinct_final),Concept=x.concept,Family=x.family,Items=x.item_count,Coverage=f'{x.respondent_coverage_n:,} ({1-x.missing_fraction:.1%})',Solo_gain=f'{x.standalone_delta_profile_r2:+.5f} [{x.standalone_ci_low:+.5f}, {x.standalone_ci_high:+.5f}]',Top5_stability=f'{x.outer_top5_frequency:.0%} outer / {x.split_top5_frequency:.0%} split'))
base_rows=[]
for name in ['bridge_only','bigfive_only','bridge_plus_bigfive','distinct_k1','distinct_k3','distinct_k4','distinct_k5','distinct_k8']:
 x=m.loc[name];base_rows.append(dict(Comparison=name,Macro_R2=f'{x.macro_r2:.5f}',Dimension_r=f'{x.macro_dimension_r:.5f}',Within_person_r=f'{x.mean_within_person_profile_r:.5f}'))
secrows=[]
for x in sec[sec.analysis.isin(['k0','k4','k5'])].itertuples():secrows.append(dict(Outcome=x.outcome,Added_k=x.analysis,R2=f'{x.macro_r2:.5f}',Delta=f'{x.delta_r2:+.5f}',Interval=f'[{x.delta_ci_low:+.5f}, {x.delta_ci_high:+.5f}]',Observed_N=x.observed_respondents))
body=f'''# AA-26 — corrected human SAPA profile information gain

## Executive takeaway

1. The five best distinct additional existing-item families are **broad negative emotionality; behavioral and emotional self-regulation (PS:S); energy and stamina; cheerfulness and amusement; and vulnerability/coping under pressure**, in that full-cohort internal-CV ordering. These are source-family subsets and future measurement candidates, not model traits.
2. **Four additions capture 96.5% of the best observed gain**; three capture 93.3%. The pre-specified .01 absolute-R² tolerance formally chooses one among positive-size sets, but even zero additions is within that tolerance. It cannot substantiate “nearly all improvement.” Four is the post hoc relative-95% answer, conditional on the evaluated candidate pool and adaptive path.
3. The four-addition selection procedure improves broad held-out macro-R² from **.19168 to .19841**, Δ **+.00673** (conditional paired-bootstrap 95% interval **[+.00580,+.00766]**). Five reaches .19865, Δ+.00697; further additions reduce performance. This is modest improvement, not recovery of a complete latent personality profile.
4. Four additions also improve the separate leakage-safe **Big Five** task by **+.05623 R²** and **HiFWB** by **+.04925 R²**. These outcomes have different baselines and observed-label samples; their larger gains do not replace the broad-profile conclusion.
5. Negative emotionality and energy/stamina are the clearest priorities for a later elicitation feasibility study. The PS:S self-regulation family has comparably stable predictive evidence, but needs source-key/content review before measure construction. Cheerfulness and vulnerability/coping are smaller, exploratory extensions. None establishes existing model representation, human equivalence, or causal utility; no elicitation was run.

## Repaired target and dependency verification — assessed before additions

The measurement gate was frozen in commit **51e5f52**, before predictive candidate ranking. It reconstructs **74 dimensions** from AA-13's 79 documented administered-source constructs, using official `superKey696.csv` signs and **7−x** for negative keys. All 41 current-bridge proxy items, all 99 official Big Five items, and all 13 frozen HiFWB items are removed from each target. Five IPIP100 Big Five dimensions then have no disjoint items and are excluded. Retain a source subset only with >=2 keyed items and >=2% respondent coverage; a respondent score needs **at least two observed items**. No one-item target score survives and no target label is imputed.

The target contains **443 unique items**, **22,349 of 23,679 respondents** with >=5 observed dimensions, and **389,072 observed target cells** in that fixed analysis cohort. Across the full raw cohort, target missingness is **77.70%**, median observed dimensions **14**, and complete 74-dimensional profiles **zero**. The exact 74 names, official source keys, all item IDs/signs, removed items, per-dimension coverage and missingness appear in [target_dimension_inventory.csv](repair/target_dimension_inventory.csv) and [measurement_freeze.json](repair/measurement_freeze.json). The score/mask/source hashes allow reconstruction without exporting respondent rows. Source-construct subsets are not independently validated full scales; validity here means faithful documented-key implementation, enforced eligibility, and disjoint evaluation.

- Raw matrix SHA256: `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`.
- Official-key SHA256: `8d19b6a23c7f42b91cf5bc0895e2c63790510ba9355a2c69d19703c6f791bc49`.
- Frozen specification SHA256: `{g['target_spec_sha256']}`.
- Cohort mask SHA256: `{g['target_eligibility_sha256']}`.
- Target observation-mask and score fingerprints: `repair/target_validity_gate.json`, `repair/target_score_fingerprint.json`.

**All five flagged dependencies materially changed**, rather than passing equivalence. The minimum-two rule for multi-item bridge proxies reduces the AA-20/24/AA-21-common mask from 2,859 to 1,179 and the AA-22/23 pre-index mask from 3,551 to 1,528. Masks were compared exactly; score tolerance was 1e−10. Only affected human analyses were refit, in **cf6ce5b**, before candidate interpretation:

| Analysis | Corrected eligible N | Test N | Corrected result |
|---|---:|---:|---|
| AA-20 | 1,179 | 243 | Beyond-Big-Five ΔR² +.0010, CI [−.0186,+.0193]; no incremental validity |
| AA-22 | 1,484 after index coverage | 301 | ΔR² +.0654, CI [+.0330,+.0976] |
| AA-23 | 1,473 after index coverage | 294 | ΔR² +.1119, CI [+.0723,+.1528] |
| AA-24 | 1,179 | 243 | ΔR² +.0006, CI [−.0188,+.0208]; no incremental validity |
| AA-21 common sensitivity only | 1,179 | 236 | Held-out R² .4853 |

AA-16–19, AA-21 primary, and AA-25 were not rerun. The legacy full-cohort item standardization in AA-22/23/24 and AA-21 common sensitivity is preserved to isolate eligibility changes, with that limitation explicit. New AA-26 predictor transformations are training-only. See [dependency_refit_report.md](dependency_repair/dependency_refit_report.md) for original recipes and rerun scope. Historical AA-12/13 invalid claims remain withdrawn: the new AA-26 target does not retrospectively restore their results. Persona transports that depend on changed human weights remain stale/withdrawn; no persona was rescored.

## Candidate pool, distinctness, and held-out design

The untouched target freeze leaves **nine eligible source families (62 unique items)** outside the target, bridge, Big Five, and HiFWB unions. Each needs >=2 keyed items, >=2 observed respondent items, and >=2% full-cohort coverage. The two-item BFAS enthusiasm remainder is excluded for only 334 observed respondents. The candidate inventory explicitly records exclusions. Exact/inverse target aliases and candidate wording pairs (including comparisons against all other administered items) at sequence similarity >=.90 were audited; none met those duplicate rules. Shared item IDs between candidate subsets are disclosed in the redundancy tables and are measured once, not called additional questions.

The pre-performance grouping rule uses documented source/facet identity, a semantic alias group for QB6 emotional stability versus EPQr negative emotionality, and training-only baseline-residual score correlations |r|>=.80 with >=100 jointly observed rows. One representative per unioned group is allowed. Sensitivity thresholds .70/.90 and an unrestricted k=1–8 diagnostic are included. Eight distinct groups were admissible in every outer fold. Emotional/behavioral content remains related; “distinct” means this operational facet/conditional-redundancy rule, not orthogonal constructs. PS:S and negative emotionality have residual |r| about .269, supporting separate information under that rule.

Five outer folds, three inner folds, seed20260919. A multi-output ridge formulation fits one coefficient vector per observed target, sharing an alpha selected by equal-dimension macro validation R² from {{1,10,100,1000}}. Item standardization, feature standardization, missing-value mean imputation and missingness indicators use training rows only. Missing outcomes never enter fitting or scoring. All comparisons use the same 22,349 respondents and fixed observed-target mask. Inner-CV greedy forward selection chooses k=1–8; outer-fold targets do not choose candidates or alpha. Secondary outcomes do not choose the broad-profile path.

Uncertainty uses 1,000 paired respondent bootstrap resamples of pooled out-of-fold errors, conditional on fitted predictions; it is not a refit bootstrap and does not account fully for overlapping CV training sets or choosing the best k. Selection stability uses five outer selections and 20 additional independent training/validation splits. Final displayed names/order come from full-cohort internal CV. **Held-out values validate an adaptive selection procedure, not an independently tested fixed final label set.** All five final top-five families appeared in every outer top-five set, while their ordering can vary.

## Broad-profile results

{table(pd.DataFrame(base_rows))}
The current bridge alone reconstructs broad observed-profile scores weakly. Big Five is a much stronger baseline; the bridge adds about .00646 R² beyond it. Candidate gains below are beyond **bridge plus Big Five**, not the weaker bridge-only baseline. Within-person correlation compares standardized dimensions only where that respondent has observed target scores; it is not a complete-profile accuracy estimate.

{table(pd.DataFrame(rows))}
Solo gains and intervals above add each family separately to the same baseline; they must not be summed. Conditional per-fold forward increments and preceding families are in `incremental_gain_by_candidate.csv`. Per-target improvements are in `dimension_improvement_by_candidate.csv`; the ranking table records improved-dimension counts, largest improvements, residual redundancy, secondary solo gains, coverage and missingness. Negative emotionality improves 51/74 dimensions, PS:S 55/74, energy 45/74, cheerfulness 35/74, and vulnerability/coping 36/74; these counts are descriptive and not multiplicity-corrected significance claims.

The unused pool is concentrated in emotionality and self-regulation because existing broad target items and bridge/BF/HiFWB items were reserved first. This is a ranking of the available unused-item pool, not proof these are the best conceivable behavioral concepts across all SAPA content. Sparse candidate coverage and observed-label coverage affect attainable gains. No claim is made about missing-not-at-random deployment or dense future questionnaires.

## Smallest useful set and stopping curve

![Held-out performance curve](minimal_set_curve.png)

{table(c[['k','profile_r2','delta_profile_r2','fraction_of_best_gain']].round(6))}
The pre-specified absolute tolerances .005/.01/.02 all choose k=1 among positive-size sets; **baseline alone is also within .01 and .02**, though not .005. One addition captures only 43.2% of the best observed gain, so it does not meet an ordinary meaning of “nearly all.” The supplemental relative-95% criterion chooses **four**; three capture 93.3%, and five yield the observed maximum. The fourth's marginal value is small and its identity/order is less stable across the extra split selections. A parsimonious future feasibility study can prioritize the strongest three and treat cheerfulness as a fourth exploratory extension. Four is an empirical near-saturation estimate, not a pre-registered superiority conclusion or a validated fixed-question-count optimum.

The full-data first four comprise negative emotionality, PS:S self-regulation, energy/stamina, and cheerfulness. Their complete existing item membership and exact key signs are in `selected_question_or_construct_set.csv`; this is four construct families, not four newly authored questions. The fifth family is vulnerability/coping under pressure. Sixth–eighth additions lower aggregate held-out performance; no expanded-set benefit is claimed. Absolute-tolerance sensitivities and .70/.90 grouping sensitivities are provided separately.

## Big Five and HiFWB secondary outcomes

{table(pd.DataFrame(secrows))}
Big Five prediction uses bridge proxies stripped of **all Big Five target items**, discarding any remainder with fewer than two items. Big Five scores never predict themselves. Its baseline R² is therefore not the broad-profile Big-Five predictor baseline. HiFWB uses the frozen 13-item outcome, bridge plus Big Five controls, and no outcome-overlapping predictors. Both secondary label definitions preserve documented fixed source scoring; official Big Five/HiFWB item standardization is frozen on the existing human cohort, whereas all fitted predictor transformations are training-only. Secondary performance uses outcome-observed rows within the same outer broad-profile folds: 22,327 respondents have at least one observed Big Five score; 8,586 have eligible HiFWB. Gains and intervals are conditional OOF comparisons, not new outcome-selected candidate rankings. Adding the fifth family does not improve HiFWB over four.

## Future elicitation evidence, source-key caveats, and CPU gate

The strongest human incremental and stability evidence supports negative emotionality, PS:S behavioral/emotional self-regulation, and energy/stamina as **topics worth studying**. PS:S's label is corrected from the frozen working label “Stress reactivity” after reviewing its broader existing wording; no scoring or grouping changed. Vulnerability/coping scores are oriented toward vulnerability. The official source also has counterintuitive signs: q_1567 “Radiate joy.” is reversed in NEOe6, while q_824 “Feel desperate.” is positive in PSs. These are faithfully retained, not silently repaired. They require source-key/content review before any future measure construction; see `candidate_label_audit.md`. Thus negative emotionality and energy are the clearest immediate design priorities, PS:S is a promising but review-dependent family, and cheerfulness/coping remain exploratory additions. The measurement gate does not certify the psychometrics of source-subset scores or every supplied key.

**CPU gate PASS:** existing local Python, small linear systems, BLAS threads limited to one. **RunPod/GPU/paid-compute/model-inference gate PROHIBITED**, regardless of statistical gain. No model activations or persona matrices were loaded, no persona scored, no new prompt/item authored, and no viewer changed. No respondent-level matrices or rows are exported.

## Reproduction and verification

Use the existing scientific environment, not a new installation. In this worktree, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /tmp/aa17venv/bin/python` runs the following scripts with `--data-dir ../assistant-axis-aa10/data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE` where supported:

1. `run_measurement_repair.py` (frozen target/eligibility; commit51e5f52).
2. `run_dependency_refits.py` (affected human blocks only; commitcf6ce5b).
3. `run_information_gain.py` (nested held-out ranking, curves, stability and secondary intervals).
4. `build_report.py` (this report and static figure; no data-directory argument).
5. `verify_information_gain.py` (source/spec/mask checks, independent reverse means, missingness, numerical ridge equivalence, train-only fit invariance, folds, distinctness, results and scope).

`verification_report.json` records the new checks. The old feasibility-only `verify_outputs.py` and blocked-state artifacts are historical and are not the current verification contract. `artifact_inventory.csv` distinguishes active results from those archived audit records and hashes all included files except itself. Research state, claims, findings, provenance, startup freshness and navigation are updated on the AA-26 branch. Model used for agent analysis: GPT-6 Astra, as explicitly requested; no separate model inference was performed.
'''
(OUT/'aa26_report.md').write_text(body)
fig,ax=plt.subplots(figsize=(8.5,4.8));ax.plot(c.k,c.profile_r2,'o-',color='#165d8d',label='Nested held-out distinct path');ax.fill_between(c.k,s['baseline_macro_r2']+c.delta_ci_low,s['baseline_macro_r2']+c.delta_ci_high,color='#165d8d',alpha=.15,label='95% interval for gain (baseline anchored)');ax.axhline(s['baseline_macro_r2'],color='#555',ls='--',lw=1,label='Bridge + Big Five');ax.axvline(4,color='#967000',ls=':',label='First k capturing ≥95% of best gain');ax.set(xlabel='Added existing construct families (k)',ylabel='Macro held-out R², 74 target dimensions',title='AA-26: modest gains level off at four to five additions',xticks=range(9));ax.grid(alpha=.15);ax.legend(fontsize=8,loc='lower right');fig.tight_layout();fig.savefig(OUT/'minimal_set_curve.png',dpi=160);fig.savefig(OUT/'minimal_set_curve.svg');plt.close(fig)
svg=OUT/'minimal_set_curve.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
(OUT/'phase_gate_audit.md').write_text('''# AA-26 corrected phase gates

| Gate | Decision | Evidence / limit |
|---|---|---|
| Frozen raw/key provenance | PASS | Exact raw/key SHA256, 23,679 × 696 |
| Reverse scoring and target eligibility | PASS | Official signs, 7−x, >=2 items; zero one-item scores |
| Disjoint target | PASS | 74 source subsets / 443 items; no bridge/BF/HiFWB/candidate overlap |
| Broad observed-profile feasibility | PASS, limited | 22,349 respondents; 77.7% missing; no complete profiles; no imputed labels |
| Full-scale psychometric validity | NOT ESTABLISHED | Subsets are not full original scales; counterintuitive source keys disclosed |
| Dependency equivalence | FAIL / REPAIRED HUMAN-ONLY | All five masks changed; targeted human refits in cf6ce5b |
| Unaffected prior analyses | PRESERVED | AA16–19, AA21 primary, AA25 not rerun |
| Historical invalid claims | WITHDRAWN | AA12/13 claims and changed-weight persona transports not restored |
| Candidate distinctness / held-out design | PASS | Source grouping, residual correlations, nested 5×3 CV, 20 stability splits |
| Smallest-set claim | QUALIFIED | .01 tolerance includes k0; relative95% selects k4, supplemental interpretation |
| Local CPU | PASS | Existing Python; one BLAS thread; no raw rows exported |
| RunPod / GPU / paid compute | PROHIBITED / NOT USED | No escalation permitted by task |
| Model inference / elicitation / persona scoring / viewers | PROHIBITED / NOT USED | Human matrices only; no new prompts |

Current numerical/source verification: `verify_information_gain.py` and `verification_report.json`. Prior blocked-state feasibility records are archived context, not current target status.
''')
print('Report and static curve rendered.')
