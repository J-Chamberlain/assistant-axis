# SAPA × HiFWB exploratory outcome-surface preservation note

Status: active exploratory preservation snapshot.

Date preserved: 2026-09-15.

Branch: `gpt/sapa-hifwb-outcome-surface`.

This directory preserves the first-pass human-only SAPA × HiFWB analysis originally executed in ChatGPT before a repository analysis freeze existed. The analysis is therefore explicitly exploratory/post hoc and must not be represented as preregistered or confirmatory.

The preserved outputs map SAPA V5 wellbeing-relevant items using the HiFWB distinction between wellbeing itself (WHAT) and content-laden predictors/causes (HOW), construct a provisional observed-item wellbeing score, audit its common-factor structure, and relate it to the already-frozen SAPA Big Five human terrain and density backbone.

Headline exploratory results from the saved report are: 13 DIRECT and 4 CLOSE wellbeing indicators; mean pairwise correlation among the 13 DIRECT indicators 0.4784; first-component variance fraction 0.5226; five-fold held-out Big Five→wellbeing Pearson r 0.6276 and R² 0.3939 for N=3,972; non-affect sensitivity r 0.6356 and R² 0.4039 for N=2,548; and Spearman association between wellbeing and frozen backbone position 0.5397, rising to 0.5555 for the non-affect sensitivity.

Boundaries: this is a static cross-sectional association; the provisional wellbeing score is not a validated HiFWB instrument; community wellbeing is poorly covered; planned missingness is substantial; no causal or transition-dynamics claim is supported; and no model geometry is involved.

Source lineage: Harvard Dataverse SAPA V5 DOI `10.7910/DVN/SD7SVE`; canonical SAPA item/scale metadata under `research/outputs/human_trait_dataset_feasibility/sapa/`; frozen Big Five terrain scoring and backbone under `research/outputs/sapa_static_human_terrain/` on `gpt/sapa-static-human-terrain`.

Reproducibility boundary: the exact chat-execution script was not preserved at run time. The saved tables/report are therefore a preservation snapshot, not a fully rerunnable analysis package. Any confirmatory continuation should first freeze the item rubric/scoring rules and then rerun from the local gitignored SAPA microdata.
