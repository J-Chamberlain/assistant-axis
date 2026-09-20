#!/usr/bin/env python3
"""Feasibility closeout; never fabricate profiles/calibration when the bridge fails."""
from pathlib import Path
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,csv,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
A=json.loads((OUT/'density_audit.json').read_text());G=json.loads((OUT/'bridge_validity_gate.json').read_text());C=pd.read_csv(OUT/'facet_bridge_coverage.csv');D=pd.read_csv(OUT/'demographic_summary.csv');M=pd.read_csv(OUT/'item_missingness.csv');H=pd.read_csv(OUT/'respondent_missingness_distribution.csv')
assert G['status']=='FAIL_UNTESTABLE_PRESENT_BRIDGE'
headers={'persona_facet_scores.csv':['model','persona','construction','facet_code','score'],'human_calibration_summary.csv':['construction','sample','n','metric','quantile','value'],'persona_profile_plausibility.csv':['model','persona','construction','global_percentile','nearest_neighbor_percentile','closest_profile_similarity','classification'],'cross_model_profile_agreement.csv':['persona','construction','qwen_class','llama_class','gemma_class','agreement']}
for name,columns in headers.items():pd.DataFrame(columns=columns).to_csv(OUT/name,index=False)
status=[]
for name in headers:status.append(dict(artifact=name,status='NOT_RUN',reason='Primary semantic bridge gate failed: Extraversion retains 2 facets; >=3 required. Empty schema, not zero-valued results.'))
for name in ['human calibration figure','facet-profile comparison figure','five supported and five outlying examples','persona-family concentration','consensus persona profile','domain agreement diagnostic']:status.append(dict(artifact=name,status='NOT_RUN',reason='No profile comparison allowed after primary semantic gate failure; no surrogate result substituted.'))
pd.DataFrame(status).to_csv(OUT/'execution_status.csv',index=False)
sens=[dict(sensitivity='direct_only_coverage',status='AUDITED',result='20 facets; N/E/O/A/C=3/2/5/6/4; primary gate fails'),dict(sensitivity='direct_plus_close_coverage',status='AUDITED',result='29 facets; N/E/O/A/C=5/6/6/6/6; cannot rescue primary'),dict(sensitivity='human_completeness_10_of10',status='AUDITED',result='117260 adults18–80; all30 facets complete'),dict(sensitivity='human_completeness_9_of10',status='AUDITED',result='237832 adults18–80; >=9 observed items on all30 facets')]
for name in ['five_domain_baseline','Qwen_Llama_Gemma_separate','consensus','human_calibrated_percentile_bootstrap','leave_one_mapped_trait_out','strict_vs_expanded_plausibility']:
 sens.append(dict(sensitivity=name,status='NOT_RUN',result='Primary semantic coverage gate failed before model scoring/human calibration'))
pd.DataFrame(sens).to_csv(OUT/'sensitivity_summary.csv',index=False)
def prose(text):
 for a,b in [('supplies307','supplies 307'),('contain307','contain 307'),('are145','are 145'),('complete30','complete 30'),('all300','all 300'),('all30','all 30'),('all7200','all 7,200'),('full7200','full 7,200'),('are182','are 182'),('retains20','retains 20'),('broader29','broader 29'),('required18','required 18'),('with18','with 18'),('aged18','aged 18'),('adults18','adults 18'),('Allowing9','Allowing 9'),('admits294','admits 294'),('and237','and 237'),('A9/10','A 9/10'),('admits237','admits 237'),('the300','the 300'),('all300','all 300'),('All300','All 300'),('has148','has 148'),('are148','are 148'),('invert148','invert 148'),('its120','its 120'),('separate20','separate 20'),('case2005','case 2005'),('The2018','The 2018'),('has333','has 333'),('item1 ','item 1 '),('column34','column 34'),('item300','item 300'),('at333','at 333'),('median1','median 1'),('percentile3','percentile 3'),('percentile8','percentile 8'),('maximum10','maximum 10'),('codes1/2','codes 1/2'),('below100','below 100'),('at items58/78/202','at items 58/78/202'),('StagesC/D','Stages C/D'),('Exact275','Exact 275'),('and240','and 240'),('all240','all 240'),('predeclared95/99','predeclared 95/99'),('6−x reversal','6−x reversal'),('148 negative','148 negative')]:text=text.replace(a,b)
 return text

def table(df):
 return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in df.itertuples(index=False,name=None))+'\n'
sex=D[(D.cohort=='complete_adults_18_80')&(D.variable=='sex_code')];country=D[(D.cohort=='complete_adults_18_80')&(D.variable=='country_reported_code')].sort_values('n',ascending=False).head(5)
summary='; '.join(f'{r.category}: {r.n:,}' for r in sex.itertuples());countries='; '.join(f'{r.category}: {r.n:,}' for r in country.itertuples())
md=f'''# AA-27 source and density audit

**Dense-reference gate passes.** Johnson's first-party repository supplies307,313 respondents ×300 item responses. There are145,388 fully complete30-facet profiles across all ages, including **117,260 adults aged18–80** under the primary frozen rule. Allowing9/10 items on every facet admits294,985 across all ages and237,832 adults. These are completeness eligibility counts before any hypothetical deduplication/splitting; no reference model or profile comparison was fitted because the semantic bridge fails.

## Source and reproduction

Primary repository: https://osf.io/tbmh5/ . Dataset component: https://osf.io/wxvth/ . Scoring component: https://osf.io/ycvdk/ . The browser fetch returned403, but the official OSF JSON API and its file-download URLs succeeded. No mirror or substituted dataset was used. Exact UTC retrieval times, filenames, URLs, byte counts and SHA256 are in `source_manifest.json`; download hashes match the OSF-provided hashes. Data selected are the300-item file from the Johnson(2014) component, not its120-item file or the separate20,993-case2005 component.

- `IPIP300.dat`,102,949,853 bytes, SHA256 `1bbb7189f5f0f2883bb4493f956cf639178c5c8ee95319fd3881f6d9d2f189a3`.
- `DAT300.doc`,54,272 bytes, SHA256 `b72ea04065dbc98c70ac69a6aa5bc58dd8896dcd33902b8d44930c58351cdb96`.
- `IPIP-NEO-ItemKey.xls`,54,784 bytes, SHA256 `d3f962e46b412151a2df571ebb5902bc0967c864ec5e05ab0a46d254dc0b52a0` (acquired source record).
- `IPIP-NEO-300 scoring tool_2.xlsx`,70,757 bytes, SHA256 `fe6365561c8f812fa2ddf305efe24f10e190ba7b8a168f48def5112753a31aff` (Input sheet used).

Official item wording and signs were independently matched against https://ipip.ori.org/newNEOFacetsKey.htm . All300 facet assignments/signs agree, with three explicitly normalized minor wording variants at items58/78/202. There are148 negative-keyed items, ten items per facet, and thirty facets. The public worksheet's population norms were not used. The original key workbook was acquired and hashed; extraction used the newer coauthored300-item scoring workbook's Input sheet and the independent official IPIP web key.

## Scoring detail that prevents double reversal

DAT300.doc states that negative-keyed items were already recoded during inventory completion. Thus the downloaded1–5 values are already oriented; **apply no second6−x reversal**. Zero means missing. A complete facet's score would be its ten oriented items' mean; the alternative averages at least nine observed items. The independent key audit verifies the original direction and synthetic/raw-category reverse roundtrip. The density audit calculates observation counts, not human facet distributions. A mistaken second reversal would invert148 items.

The2018 documentation correction removed two leading blank columns from the data. The acquired version has333 content bytes per record, with item1 at one-based column34 and item300 at333; the independent parser validates every line. CASE/time fields are not retained in outputs.

## Coverage and demographics

Overall item missingness: **{A['overall_missing_fraction']:.3%}**. Across respondents, missing-item median1,90th percentile3,99th percentile8, maximum10. Item-specific missingness ranges from{M.missing_fraction.min():.3%} to{M.missing_fraction.max():.3%}. `item_missingness.csv` reports all300 items; `respondent_missingness_distribution.csv` is a histogram, not respondent rows; `human_facet_eligibility.csv` reports coverage per facet.

Complete-adult reported sex counts: {summary}. Sex codes1/2 are documented as male/female. Age bands and reported country codes are summarized in `demographic_summary.csv`. Most frequent complete-adult country-code groups: {countries}. Blank and small country cells below100 are aggregated, not individually exposed. Country codes are retained as reported, without inventing a nationality recoding. No representativeness claim follows from these counts.

This is a self-selected internet reference sample described in Johnson's repository, not a representative population sample. The freeze uses completion and age, with no post hoc removal based on unusual profile content and no claim to reproduce published quality-filtered norm samples. Possible careless responses, repeat participants, nonindependence and demographic selection would limit any later comparison. The contemplated split would deduplicate exact item patterns first, but was **not executed** after the semantic gate failure.

## Reuse and privacy

The official IPIP permission page (https://ipip.ori.org/newPermission.htm) places the items/scales/inventories in the public domain. The OSF parent and dataset node are public and explicitly make the data available for the cited research; their `node_license` fields are null. No separate dataset license was found in retrieved metadata/documentation. **Item public-domain status is not represented as an explicit dataset license.** Raw data and source workbooks stay in gitignored `data_external/aa27_ipip_neo/`; no human rows, CASE IDs, human profile vectors or nearest-neighbor records are committed. All analysis is local CPU.
'''
(OUT/'dataset_audit.md').write_text(prose(md))
body=f'''# AA-27 — dense human profile plausibility: presently untestable

**We cannot yet determine whether the model personas form personality configurations that humans actually exhibit.** The dense human reference is available and adequate, but the present model-trait bridge fails the frozen coverage requirement. This feasibility result separates a solvable measurement gap from evidence about unusual persona configurations: it does **not** show that the personas are psychologically implausible.

Johnson's first-party IPIP-NEO-300 data contain307,313 respondents, including **117,260 adults with all300 responses and all30 facets complete**. The strict semantic bridge retains20 facets, but only **two Extraversion facets** have at least two nonduplicate direct model-trait indicators. The frozen gate required18 facets overall and at least three in every Big Five domain. Accordingly, no persona facet scores, human distances, outlier percentiles or supported/outlying classifications were calculated. The broader29-facet construction is a sensitivity mapping and cannot replace the failed primary bridge.

## Source and scoring first

The [Johnson repository](https://osf.io/tbmh5/) supplies both response data and scoring documentation through its first-party API. All downloaded OSF file hashes agree with the archive metadata. The300-item response file is dense:0.403% missing item cells;145,388 complete respondents across all ages;117,260 complete adults18–80. A9/10-per-facet completeness allowance admits237,832 adults. No broad profile imputation was performed. Detailed provenance, missingness, demographic composition, reuse conditions, source versions and hashes are in [dataset_audit.md](dataset_audit.md) and `source_manifest.json`.

The critical scoring detail is that **the released file already reverse-scores negative items**. The300-item official key has148 negative keys. All300 facet assignments and signs were cross-checked against the [official IPIP key](https://ipip.ori.org/newNEOFacetsKey.htm); the downloaded data must not be reversed a second time. Three small wording differences were normalized explicitly; no key signs were inferred. The source is a dense internet sample, not automatically a population reference.

## Frozen bridge result

{table(pd.DataFrame(G['domain_coverage']).rename(columns={'domain':'Domain','strict_facets':'Direct-only facets','expanded_facets':'Direct+close facets','required':'Required'}))}

The full7200-row crosswalk covers every canonical model trait × every IPIP facet. It records canonical definition, polarity, tier, semantic rationale, source, same-pole alias group, confidence and inclusion in each construction. There are182 explicitly adjudicated candidate pairs; other prior proposals remain excluded broad candidates and unmatched pairs are explicit none. This is one Astra semantic review, not inter-rater validation. All model-trait definitions and prior AA21/25 facet assignments come from pinned base91ad751 artifacts; no human correlations, HiFWB results, persona numeric values, or desired classifications selected mappings.

Direct means explicit correspondence to the official facet item content. Close mappings require an additional semantic inference. Broad-domain similarity is insufficient for a direct facet measure. The previous AA25 mapping was useful candidate evidence but was designed for broad domains, and its “direct” labels were not automatically inherited as facet-valid. Within each facet, same-pole near-aliases collapse deterministically to one representative. Opposite-pole traits are not automatically collapsed. Multiple retained direct mappings from the same trait to different facets are disclosed and would require interpretation of shared-indicator dependence; no covariance-based pruning was attempted.

Extraversion is the decisive shortfall:

| Facet | Nonduplicate direct indicators | Status |
|---|---|---|
| E1 Friendliness | avoidant− | One indicator; charismatic/flirty/nurturing are close only |
| E2 Gregariousness | gregarious+ | One indicator; extroverted/introverted definitions are close only |
| E3 Assertiveness | assertive+, dominant+, submissive− | Retained |
| E4 Activity Level | none | Animated/effusive describe expressive energy, not being busy/active; close only |
| E5 Excitement-Seeking | adventurous+ | One indicator; instrumental risk-taking need not mean seeking thrills |
| E6 Cheerfulness | entertaining+, optimistic+, serious− | Retained after humor-alias collapse |

A measured facet needs at least two nonduplicate traits. Adding close indicators produces six Extraversion facets, but doing so as the primary would relax the rule after coverage inspection. The other strict gaps are N2 anger, N4 self-consciousness, N5 immoderation, O2 artistic interests, C1 self-efficacy and C5 self-discipline. Exact counts, rejected aliases and one-sided flags are in `facet_bridge_coverage.csv`. Strict retained one-sided facets are listed there; they are not treated as fully bipolar measures.

![Frozen semantic coverage, not profile plausibility](facet_bridge_coverage.png)

## What was deliberately not run

The primary coverage failure stops StagesC/D. No facet values were constructed for Qwen, Llama or Gemma, no consensus profiles were calculated, and no five-domain agreement diagnostic was used to rescue the mapping. Exact275-persona and240-trait source schema/alignment and source hashes are verified separately using names/headers only; numeric cells are not evaluated. These alignment checks are provenance checks, not evidence of cross-model profile agreement.

No human reference/calibration/held-out split was made, no Mahalanobis or nearest-neighbor landscape was fitted, and no empirical percentile or persona classification exists. Cross-model agreement, family concentration, illustrative supported/outlying profiles, calibrated percentile bootstrap, five-domain plausibility comparison and leave-one-trait-out sensitivity are **not run**, not zero or negative results. Required downstream CSVs contain headers only and are paired with `execution_status.csv`. Requested calibration and facet-profile comparison figures are not fabricated; the two delivered figures show density and semantic coverage only.

![Human item completeness, not calibrated distance](human_density_distribution.png)

The conditional analysis specification remains frozen in `analysis_freeze.md`: independent human reference/calibration/held-out sets, marginal rank normalization, human-calibrated regularized global and local distances, predeclared95/99-percentile thresholds, consensus checks, and focused sensitivities. It is a future reproducible specification, not an executed analysis. The freeze documents incidental exposure to published workbook example norms during sheet inspection; those norms were not the acquired cohort's distributions and were not used in any semantic decision or calculation.

## Interpretation and next step

**Presently untestable with this direct semantic bridge.** Human data availability is no longer the barrier. A later authorized study would need independently defensible direct indicators for at least one additional Extraversion facet, without duplicating existing aliases, plus validation of the retained facet constructions and one-sided/shared indicators. This audit does not authorize new trait extraction, prompts or model inference. It also does not prove that the existing trait collection lacks every possible adequate crosswalk: the result is conditional on the explicit conservative semantic judgments, which remain reviewable.

If independently reviewed mappings change, freeze a new version before looking at profile comparisons; never change them to obtain plausible personas. Even a future passing analysis could support only relative trait combinations within a sample-conditional facet space, not absolute score equivalence, population prevalence, simulated human behavior, causal/longitudinal validity, subjective wellbeing or validity of all240 traits. No HiFWB scoring or intervention analysis occurred.

## Verification, artifacts and provenance

Model used: **GPT-6 Astra; High thinking**, as requested. Infrastructure policy commit **6d564c3** preceded substantive work. Scoring/crosswalk/coverage freeze commit **79417c2** preceded human response auditing and model-source schema checks. Branch: **codex/aa27-ipip-neo-profile-plausibility**, base **91ad7519fe89b55921f58680a9a734e158320ca4**. The completion commit is the commit containing this report; `git log -1 -- aa27_report.md` resolves it.

`verify_aa27.py` checks source/freeze hashes, all300 official key assignments/signs, two independent eligibility parsers, missingness reconciliation, all7200 judgments, nonduplicate selection, the failed gate, exact source alignment, preserved AA16–26 artifacts, and the absence of respondent-level outputs. Deterministic reruns compare aggregate-output hashes. Split separation, metric calibration and persona bootstrap checks are marked not applicable because the gate correctly prevented those operations. `verification_report.json`, `deterministic_rerun_verification.json`, `closeout_verification.json` and `artifact_inventory.csv` distinguish these checks from unexecuted validation.

Generating scripts: `acquire_sources.py`, `extract_scoring_spec.py`, `build_crosswalk.py`, `audit_dataset.py`, `build_feasibility_report.py`, `verify_aa27.py`. Scoring-workbook extraction uses the bundled Python/openpyxl in read-only mode; no spreadsheet is authored or recalculated. Aggregate numerical audit/figures use the existing local scientific environment. No new installation or paid compute was needed. Raw sources are gitignored and only aggregate human counts are saved. AA16–26 artifacts remain untouched. Canonical findings, claims, provenance, state, thread-start, startup manifest, research index, navigation/file/raw-URL indexes, and runtime current results are updated.
'''
(OUT/'aa27_report.md').write_text(prose(body))
fig,ax=plt.subplots(figsize=(8,4.5));ax.bar(H.missing_item_count,H.respondents/1000,color='#296388');ax.set(xlabel='Missing item responses per respondent',ylabel='Respondents (thousands)',title='Johnson IPIP-NEO-300: dense human data are available',xticks=range(11));ax.text(.98,.95,'145,388 fully complete profiles, all ages\n117,260 fully complete adults aged 18–80',transform=ax.transAxes,ha='right',va='top',fontsize=10);fig.tight_layout();fig.savefig(OUT/'human_density_distribution.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4.5));df=pd.DataFrame(G['domain_coverage']);x=np.arange(5);ax.bar(x-.18,df.strict_facets,width=.36,label='Direct only',color='#296388');ax.bar(x+.18,df.expanded_facets,width=.36,label='Direct + close (sensitivity only)',color='#a0bdce');ax.axhline(3,ls='--',color='#963c2c',label='Required per domain');ax.set(xticks=x,xticklabels=['N','E','O','A','C'],ylabel='Facets with ≥2 nonduplicate indicators',title='Primary bridge fails Extraversion coverage',ylim=(0,7));ax.legend(fontsize=9,loc='upper left',ncol=2);fig.tight_layout();fig.savefig(OUT/'facet_bridge_coverage.png',dpi=160);plt.close(fig)
print('Feasibility report and density/coverage figures generated; persona outputs explicitly NOT_RUN.')
