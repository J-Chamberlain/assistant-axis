#!/usr/bin/env python3
raise SystemExit("Deprecated by scripts/repair_aa11_liss_package.py; running this historical builder would overwrite repaired AA-11 artifacts.")
"""Build the AA-11 pre-data LISS/HiFWB planning package."""
from pathlib import Path
import csv, json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/outputs/liss_hifwb_prior_evidence"
OUT.mkdir(parents=True, exist_ok=True)

def write_csv(name, header, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

write_csv("prior_study_crosswalk.csv", ["study","year","source_url","doi","sample","design","personality","wellbeing","method","main_result","hifwb_relevance","limitations"], [
 ["Lamers et al.",2012,"https://research.utwente.nl/en/publications/differential-relationships-in-the-association-of-the-big-five-per/","10.1016/j.jrp.2012.05.012","N=1161","cross-sectional","Big Five","positive mental health / psychopathology","multiple regression","Emotional Stability related to psychopathology; Extraversion and Agreeableness uniquely related to positive mental health","affect; psychological; social","Prior association study; not a HiFWB scoring key or human/model correspondence test"],
 ["Hounkpatin et al.",2018,"https://pubmed.ncbi.nlm.nih.gov/28921998/","10.1037/pspp0000161","N=8320","4 assessments over 8 years","repeated Big Five","life satisfaction","latent growth/change SEM","Within-person life-satisfaction change and trait change show prospective associations; direction is design-specific","appraisal; self-concept","Longitudinal human-only; no model comparison"],
 ["Fetvadjiev & He",2019,"https://pubmed.ncbi.nlm.nih.gov/30394770/","10.1037/pspp0000212","N=11890 across 5 waves","5-wave longitudinal","Big Five","positive affect; negative affect; life satisfaction; self-esteem","latent state-trait and random-intercept cross-lagged models","Traits predict wellbeing, especially affective aspects, with reciprocal/temporal caveats","affect; appraisal; self-concept","Longitudinal human-only; erratum exists (10.1037/pspp0000246)"],
 ["Lamers et al.",2011,"https://doi.org/10.1002/jclp.20741","10.1002/jclp.20741","N=1662 LISS","psychometric validation","none as predictor","MHC-SF","CFA; reliability","Three-factor emotional/psychological/social structure; high internal and moderate test-retest reliability","measurement structure only","Does not test Big Five associations or HiFWB correspondence"],
 ["Joshanloo & Lamers",2016,"https://research.utwente.nl/en/publications/reinvestigation-of-the-factor-structure-of-the-mhc-sf-in-the-neth/","10.1016/j.paid.2016.02.089","N=1662","psychometric comparison","none as predictor","MHC-SF","CFA vs ESEM","ESEM fits better and reduces factor correlations relative to CFA","measurement structure only","Structure audit; not a causal or model-correspondence study"],
])

write_csv("prior_study_findings.csv", ["study","finding_type","finding","what_future_liss_reanalysis_would_add","caution"], [
 ["Lamers 2012","association","Big Five profiles relate differentially to positive mental health and psychopathology","A preregistered LISS HiFWB measurement and prediction audit with explicit lenses and out-of-sample checks","Cross-sectional association is not correspondence or causation"],
 ["Hounkpatin 2018","longitudinal","Life-satisfaction and trait changes are prospectively related across repeated assessments","A harmonized repeated-wave plan can test temporal ordering and measurement equivalence","Do not infer a universal direction from one SEM specification"],
 ["Fetvadjiev & He 2019","longitudinal","Traits predict wellbeing, strongest for affective components, in state-trait/RI-CLPM analyses","A common-feature LISS package can separate affect overlap from appraisal and psychological/social outcomes","Wave attrition and construct overlap remain important"],
 ["Lamers 2011","measurement","MHC-SF emotional/psychological/social factors show reliability and a three-factor structure","Use as measurement context, not as an automatic HiFWB scoring key","CFA structure is not the only admissible model"],
 ["Joshanloo & Lamers 2016","measurement","ESEM improves fit and lowers factor correlations versus CFA","Pre-register competing measurement structures before fitting","ESEM result does not establish human/model homology"],
])

contents = [
 ["h","hierarchy","HiFWB hierarchy/ontology","active; analytic ontology only","not an official scale or established score"],
 ["subjective_wellbeing","content","Affect","covered","positive and negative affect; happiness"],
 ["subjective_wellbeing","content","Appraisal","covered","life satisfaction"],
 ["psychological_wellbeing","content","Meaning-making","covered","meaning/purpose"],
 ["psychological_wellbeing","content","Self-concept","covered","self-acceptance, mastery, growth"],
 ["social_wellbeing","content","Community","covered","belonging, contribution, social contact"],
 ["social_wellbeing","content","Interpersonal relationships","covered","relatedness, support, love/sorrow sharing"],
 ["subjective_wellbeing","characteristic","positive affect","mapped","direct/near-direct item evidence"],
 ["subjective_wellbeing","characteristic","negative affect","mapped","cp20l146-cp20l165 PANAS"],
 ["subjective_wellbeing","characteristic","life satisfaction","mapped","SWLS and 0-10 satisfaction items"],
 ["psychological_wellbeing","characteristic","meaning/purpose","mapped","MHC-SF-R meaning items"],
 ["psychological_wellbeing","characteristic","personal growth","mapped","MHC-SF-R develop-self item"],
 ["psychological_wellbeing","characteristic","self-acceptance","mapped","MHC-SF-R acceptance item"],
 ["psychological_wellbeing","characteristic","mastery/self-efficacy","mapped","MHC-SF-R mastery item"],
 ["social_wellbeing","characteristic","social integration/belonging","mapped","group/relatedness items"],
 ["social_wellbeing","characteristic","social contribution","mapped","valuable/can-mean-something items"],
 ["social_wellbeing","characteristic","relationship quality","mapped","social contacts and love/sorrow"],
 ["social_wellbeing","characteristic","social connection","mapped","relatedness item"],
 ["social_wellbeing","characteristic","perceived support","mapped","count-on-others item"],
 ["social_wellbeing","characteristic","social acceptance","excluded","not treated as core HiFWB lens"],
 ["social_wellbeing","characteristic","social coherence/actualization","excluded","traditional MHC-SF labels not automatic equivalence"],
 ["psychological_wellbeing","characteristic","Ryff autonomy","excluded","not in the 2020 MHC-SF-R block"],
 ["subjective_wellbeing","characteristic","interested in life","ambiguous","retain as sensitivity/ambiguity, not direct core"],
]
write_csv("hifwb_node_evidence_matrix.csv", ["node","node_type","label","status","evidence_or_rule"], contents)

items = {
2:("happy","Affect","DIRECT","happiness"),3:("interested in life","Affect","PARTIAL","ambiguous"),4:("satisfied with life","Appraisal","DIRECT","life satisfaction"),5:("valuable contribution to society","Community","DIRECT","social contribution"),6:("country developing well","Community","NON_CORE_EXCLUDED","social actualization/coherence"),7:("accept others as they are","Community","NON_CORE_EXCLUDED","social acceptance"),8:("belong to a group","Community","CLOSE","belonging"),9:("understand how society works","Community","NON_CORE_EXCLUDED","social coherence"),10:("accept myself as I am","Self-concept","DIRECT","self-acceptance"),11:("mastery of my life","Self-concept","DIRECT","mastery/self-efficacy"),12:("share love and sorrow with some people","Interpersonal relationships","DIRECT","relationship quality"),13:("develop myself","Self-concept","DIRECT","personal growth"),14:("dare to express my ideas","Self-concept","NON_CORE_EXCLUDED","not core HiFWB"),15:("life has meaning","Meaning-making","DIRECT","meaning/purpose"),16:("can mean something to others","Community","CLOSE","social contribution"),17:("satisfied with social contacts","Interpersonal relationships","CLOSE","relationship quality"),18:("feel related to other people","Interpersonal relationships","CLOSE","social connection"),19:("count on others to help me","Interpersonal relationships","DIRECT","perceived support")}
rows=[]
for version, lo, hi, period in [(1,2,19,"past week"),(1,20,25,"past month"),(2,26,39,"past month"),(3,40,53,"past week"),(4,54,71,"past month")]:
    for var in range(lo,hi+1):
        base = var if version==1 and var<=19 else ((var-24) if version==1 else (var-24 if version==2 else var-38 if version==3 else var-52))
        if base in items:
            text,lens,judgment,characteristic=items[base]
        else:
            text,lens,judgment,characteristic=("routed duplicate of MHC-SF-R item","see source item","ROUTING_ONLY","see source item")
        rows.append([f"ss20a{var:03d}",version,period,base,text,lens,judgment,characteristic,"0-5 frequency response; preserve routing"])
write_csv("liss_2020_mhc_hifwb_item_crosswalk.csv", ["variable","version","timeframe","source_item","item_text","hifwb_content","judgment","characteristic","scale"], rows)

write_csv("liss_2020_hifwb_coverage_summary.csv", ["hifwb_lens","content","mapped_unique_source_items","mapped_routed_variables","status","notes"], [
 ["Subjective wellbeing","Affect","2","9","covered","happy; interested in life; affect sensitivity from PANAS"],
 ["Subjective wellbeing","Appraisal","1","4","covered","satisfied with life"],
 ["Psychological wellbeing","Meaning-making","1","4","covered","life has meaning"],
 ["Psychological wellbeing","Self-concept","4","16","covered","accept self; mastery; growth; non-core expressive item excluded"],
 ["Social wellbeing","Community","5","20","covered","belonging/contribution; social acceptance/coherence exclusions retained"],
 ["Social wellbeing","Interpersonal relationships","4","16","covered","support, relatedness, contacts, love/sorrow"],
])

write_csv("liss_2020_variable_manifest.csv", ["variable_block","range","instrument_or_role","scale","routing_or_missing","analysis_role","source_url"], [
 ["cp20l010","cp20l010","happiness","0-10","-9 don't know; inspect other negative codes","wellbeing outcome","https://www.dataarchive.lissdata.nl/study-units/view/965"],
 ["cp20l011","cp20l011","life satisfaction","0-10","-9 don't know; inspect other negative codes","wellbeing outcome","https://www.dataarchive.lissdata.nl/study-units/view/965"],
 ["cp20l012-013","cp20l012-cp20l013","mood state/trait","1-7","official missing codes","wellbeing sensitivity","https://www.dataarchive.lissdata.nl/hosted-files/download/5031"],
 ["cp20l014-018","cp20l014-cp20l018","SWLS/Diener","1-7","official missing codes","appraisal outcome","https://www.dataarchive.lissdata.nl/hosted-files/download/5031"],
 ["cp20l020-069","cp20l020-cp20l069","BIG-V / IPIP-Goldberg Big Five","1-5","official missing codes; reverse key frozen after codebook audit","personality predictors","https://www.dataarchive.lissdata.nl/hosted-files/download/5031"],
 ["cp20l070-079","cp20l070-cp20l079","Rosenberg self-esteem","1-7","official missing codes","self-concept outcome","https://www.dataarchive.lissdata.nl/hosted-files/download/5031"],
 ["cp20l135","cp20l135","Inclusion of Other in Self","1-7 pictorial","official missing codes","social sensitivity","https://www.dataarchive.lissdata.nl/hosted-files/download/5031"],
 ["cp20l146-165","cp20l146-cp20l165","PANAS current affect","1-7","official missing codes","affect outcome/sensitivity","https://www.dataarchive.lissdata.nl/hosted-files/download/5031"],
 ["cp20l198-207","cp20l198-cp20l207","LOT-R optimism","1-5","official missing codes","psychological sensitivity","https://www.dataarchive.lissdata.nl/hosted-files/download/5031"],
 ["ss20a001","ss20a001","randomized version","1-4","constructed routing field","routing covariate","https://www.dataarchive.lissdata.nl/hosted-files/download/6031"],
 ["ss20a002-071","ss20a002-ss20a071","MHC-SF-R 18 items, routed","0-5 frequency","version/timeframe-specific; page-level missing","HiFWB outcome candidates","https://www.dataarchive.lissdata.nl/hosted-files/download/6031"],
])

(OUT/"prior_evidence_report.md").write_text("""# Prior evidence report: LISS HiFWB pre-data package\n\n## Scope\nThis is a continuity and execution-planning artifact. It records prior direct personality/wellbeing evidence and a conservative HiFWB ontology; it does not analyze respondents, choose thresholds, or claim human/model equivalence.\n\n## What prior studies establish\nLamers et al. (2012) provides a direct cross-sectional Big Five–positive-mental-health precedent. Hounkpatin et al. (2018) and Fetvadjiev & He (2019) provide repeated-wave human-only precedents linking personality change or trait levels with life satisfaction and affective wellbeing. Lamers et al. (2011) and Joshanloo & Lamers (2016) are measurement-structure precedents for the MHC-SF, including the caution that ESEM can fit differently from a constrained CFA.\n\n## HiFWB mapping\nThe hierarchy is an analytic ontology: subjective wellbeing (Affect, Appraisal), psychological wellbeing (Meaning-making, Self-concept), and social wellbeing (Community, Interpersonal relationships). Traditional MHC-SF subscales are not automatically equivalent to these lenses. The 2020 MHC-SF-R block gives coverage with direct, close, partial, and explicitly excluded judgments recorded in the crosswalk.\n\n## Epistemic status\n**Observed:** existing model-side analyses establish substantial cross-model convergence in persona geometry across Qwen 3 32B, LLaMA 3.3 70B, and Gemma 2 27B. **Interpretation:** persona geometry appears constrained rather than arbitrary across these models. **Hypothesis:** recurring model geometry may reflect durable statistical organization in human behavioral variation or human-generated behavioral language. **Unknown:** whether corresponding organization occurs in human respondent data, whether dimensions are homologous, causal origin, and generalization across families, architectures, scales, languages, or training regimes.\n\n## What a future LISS reanalysis could add\nA future, access-authorized analysis could freeze a common feature/profile representation, verify measurement structure, and test preregistered associations and correspondence. It would add direct human-data evidence to a model-side hypothesis, not retroactively validate the model geometry.\n""", encoding="utf-8")
(OUT/"hifwb_mapping_rubric.md").write_text("""# HiFWB mapping rubric (AA-11)\n\nThis rubric is an analytic mapping aid, not an official HiFWB scoring key.\n\n- **DIRECT:** item wording directly represents the named characteristic and its lens.\n- **CLOSE:** defensible adjacent representation; retain as secondary/sensitivity evidence.\n- **PARTIAL/AMBIGUOUS:** plausible but insufficiently specific; do not use as a core score without a later decision.\n- **NON_CORE_EXCLUDED:** retain for audit transparency but do not treat as core HiFWB evidence.\n\nMap multivariate behavioral signatures, not one-to-one trait names. Do not force traditional MHC-SF emotional/psychological/social subscales into HiFWB lenses. The shared human/model feature space remains deliberately unresolved in AA-11.\n""", encoding="utf-8")

(OUT/"source_manifest.json").write_text(json.dumps({"package":"AA-11 LISS pre-data HiFWB crosswalk","date":"2026-09-15","status":"active","sources":[{"study":"LISS Personality 2020","url":"https://www.dataarchive.lissdata.nl/study-units/view/965","data_filename":"cp20l_EN_1.0p.dta","codebook":"https://www.dataarchive.lissdata.nl/hosted-files/download/5031","doi":"10.17026/dans-z2c-fzcd"},{"study":"LISS Social Science 2020 MHC-SF-R","url":"https://www.dataarchive.lissdata.nl/study-units/view/1105","data_filename":"ss20a_EN_1.0p.dta","codebook":"https://www.dataarchive.lissdata.nl/hosted-files/download/6031","doi":"10.17026/dans-25d-n6kr"}],"data_access":"No respondent data supplied or accessed; files expected only after Centerdata authorization under gitignored data_external/liss_2020/"},indent=2)+"\n",encoding="utf-8")

(OUT/"liss_2020_measurement_notes.md").write_text("""# LISS 2020 measurement notes\n\nStudy 965 (Personality, May–June 2020) reports selected 6969, nonresponse 1046, response 5923, complete 5859. Expected data file: `cp20l_EN_1.0p.dta`; join key: `nomem_encr`; codebook: `codebook_cp20l_EN_1.1.pdf`. Blocks are cp20l010–011 happiness/satisfaction (0–10), cp20l012–013 mood (1–7), cp20l014–018 SWLS (1–7), cp20l020–069 BIG-V (1–5), cp20l070–079 Rosenberg (1–7), cp20l135 IOS (1–7), cp20l146–165 PANAS (1–7), and cp20l198–207 LOT-R (1–5).\n\nStudy 1105 (Social Science, May 2020) reports selected 3571, nonresponse 847, response 2724, complete 2719. Expected data file: `ss20a_EN_1.0p.dta`; join key `nomem_encr`; codebook `codebook_ss20a_EN_1.0.pdf`. `ss20a001` randomizes four versions: v1 `002–019` past week plus `020–025` past month; v2 `026–039` past month; v3 `040–053` past week; v4 `054–071` past month. Responses are 0–5 frequency categories. Preserve version/timeframe; do not pool without measurement checks.\n\nThe codebook PDF contains a `nomem_encr2` typo in one passage; the study join key and footnote use `nomem_encr`.\n""",encoding="utf-8")

(OUT/"liss_2020_hifwb_analysis_specification.md").write_text("""# LISS 2020 HiFWB analysis specification (pre-data freeze)\n\nThis is an execution-ready shell, not an executed analysis. Predictors are the 50 BIG-V items (`cp20l020–069`) with codebook-audited reverse scoring and observed-score composites; no imputation is authorized. Outcomes are routed MHC-SF-R items plus declared sensitivity measures, indexed to HiFWB content/lens. Eligibility requires valid predictor scores and at least one valid outcome; exact minimum-valid rules are frozen in the scoring manifest before data arrival.\n\nPlanned model sequence: P0 separate Big Five linear associations; P1 one-dimensional backbone only if independently predeclared; P2 Ridge on five standardized domains; P3 RBF-kernel sensitivity. Use nested cross-validation, deterministic seeds, and an affect-overlap sensitivity. Competing measurement structures (general, correlated HiFWB contents, higher-order, bifactor/ESEM where identified) must be compared before interpreting latent scores. No human/model common feature space is selected here.\n""",encoding="utf-8")
(OUT/"liss_2020_scoring_freeze.json").write_text(json.dumps({"status":"pre_data_frozen","date":"2026-09-15","respondent_data_loaded":False,"join_key":"nomem_encr","data_dir":"data_external/liss_2020/","rules":{"no_imputation":True,"no_ids_in_tracked_outputs":True,"preserve_ss20a_version_and_timeframe":True,"bigfive_reverse_key":"freeze from official cp20l codebook before scoring","minimum_valid_items":"must be finalized from codebook and recorded before data arrival","common_feature_space":"deliberately unresolved"}},indent=2)+"\n",encoding="utf-8")

write_csv("liss_longitudinal_wave_inventory.csv", ["domain","study_id","wave_or_parent","official_url","data_filename","codebook","field_period","status","note"], [
 ["Personality","16","parent","https://www.dataarchive.lissdata.nl/study-units/view/16","","","","unresolved","Official page title observed as Work and Schooling; do not infer parent identity"],
 ["Personality","15","wave 1","https://www.dataarchive.lissdata.nl/study-units/view/15","cp08a_1p_EN.dta","codebook_cp08a_EN_1.1.pdf","2008","verified metadata",""],
 ["Personality","289","wave 5","https://www.dataarchive.lissdata.nl/study-units/view/289","cp12e_1.0p_EN.dta","codebook_cp12e_EN_1.0","","verified metadata","short version routing noted as cp12e197"],
 ["Personality","965","wave 12","https://www.dataarchive.lissdata.nl/study-units/view/965","cp20l_EN_1.0p.dta","codebook_cp20l_EN_1.1.pdf","May–June 2020","verified metadata","AA-11 primary crosswalk"],
 ["Personality","1764","wave 18","https://www.dataarchive.lissdata.nl/study-units/view/1764","cp26r_EN_1.0p.dta","codebook_cp26r_EN_1.0.pdf","May–June 2026","verified metadata","future metadata only"],
 ["Mental Health","101","parent","https://www.dataarchive.lissdata.nl/study-units/view/101","","","2007–2009","verified metadata","DOI 10.17026/dans-z99-f3vd"],
 ["Mental Health","102","wave 1","https://www.dataarchive.lissdata.nl/study-units/view/102","ai07a_EN_1.0p.dta","codebook_ai07a_EN_1.0.pdf","Dec 2007–Jan 2008","verified metadata","ai07a001 random sequence"],
])
(OUT/"liss_longitudinal_measure_equivalence.csv").write_text("domain,measure,earliest_wave,latest_wave,equivalence_status,decision\nPersonality,Big Five,15,965,unknown,resolve item/version equivalence before longitudinal fit\nWellbeing,MHC-SF/MHC-SF-R,101,1105,unknown,obtain authorized files and establish overlap\nWellbeing,life satisfaction,15,965,partial,check exact wording and response scale\n",encoding="utf-8")
(OUT/"liss_longitudinal_overlap_plan.md").write_text("""# Longitudinal overlap plan\n\nDo not select a final panel until authorized files and exact codebooks are available. The smallest adequate within-person design needs at least two personality waves and two wellbeing waves with respondent overlap, baseline wellbeing, and measurement-equivalence checks. The ID-16 parent-page title discrepancy is an explicit blocker to assuming a personality parent.\n""",encoding="utf-8")
(OUT/"liss_data_access_handoff.md").write_text("""# LISS data-access handoff\n\nAfter Centerdata approval, place exact files `cp20l_EN_1.0p.dta` and `ss20a_EN_1.0p.dta` plus their official codebooks in gitignored `data_external/liss_2020/`. Compute and record SHA256 on arrival; do not upload, redistribute, or commit respondent data. Use `nomem_encr` only locally for the authorized join. Until files arrive, all execution scripts must fail cleanly and no analysis is unlocked.\n""",encoding="utf-8")

inv_header=["path","status","artifact_type","source_or_role","commit_introduced"]
inv_rows=[]
for p in sorted(OUT.rglob("*")):
    if p.is_file(): inv_rows.append([str(p.relative_to(ROOT)),"active","pre-data planning/execution artifact","AA-11 LISS HiFWB package","PENDING"])
for name in ["validate_liss_2020_schema.py","verify_liss_2020_sources.py","score_liss_bigfive.py","score_liss_hifwb.py","fit_liss_hifwb_measurement_models.py","fit_liss_personality_wellbeing_models.py","run_liss_2020_hifwb.py"]:
    inv_rows.append([f"scripts/{name}","active","execution script","AA-11 LISS HiFWB package","PENDING"])
write_csv("artifact_inventory.csv",inv_header,inv_rows)
