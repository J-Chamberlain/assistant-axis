# Occupation-Population Persona Join

## Summary

This exploratory audit joins Assistant Axis persona roles to public U.S. occupational employment statistics only when a defensible modern SOC mapping exists. It is not Paper 1.5 claim material unless independently replicated and sharpened.

## Sources

- Geometry: `research/geometry_tables/qwen_role_pc_rankings.csv`, `research/geometry_tables/cluster_membership_table.csv`, and `research/outputs/cross_model_cluster_topology/per_model_cluster_assignments.csv`.
- Occupation data: BLS OEWS national cross-industry estimates, May 2025, queried through the BLS public API.
- Documentation: `https://download.bls.gov/pub/time.series/oe/oe.txt` and `https://download.bls.gov/pub/time.series/oe/oe.datatype`.

## Coverage

- Total roles: 275
- Exact occupational matches: 47
- Close occupational matches: 26
- Broad occupational-family matches: 25
- Ambiguous occupational mappings, excluded from quantitative analysis: 25
- Unmatched / intentionally not forced: 152
- Quantitative exact+close roles: 73
- Quantitative exact+close+broad roles: 98
- Included roles with returned/cached BLS employment count: 50
- Included roles with returned/cached BLS annual median wage: 42

Note: direct scripted downloads from the BLS bulk ZIP/text hosts returned HTTP 403 in this environment, and the unauthenticated BLS API hit a daily threshold during the run. The script is rerun-safe and preserves previously fetched official BLS values, but the quantitative subset remains smaller than the mapping subset until a full API refresh or manual XLSX download is available.

## Main Observations

### Observed

- A minority of persona roles map cleanly to modern U.S. occupations. Mythic, symbolic, animal, collective, developmental, and archetypal roles remain explicitly unmatched.
- The matched subset is cluster-skewed toward procedural/professional, editorial, media/creative, and grounded service roles.
- Correlations between log employment count and persona PCs are exploratory and sensitive to whether broad mappings are included.

### Inferred

- Occupational prevalence does not provide a clean, strong explanation of persona geometry in this first pass. Where correlations appear, they should be treated as small-sample pattern hints over a filtered occupational subset.
- High-PC1 procedural roles include both common and specialized occupations; real-world prevalence is not equivalent to assistant-axis/procedural centrality.

### Speculative

- If future work uses occupation prevalence at all, it should separate occupational institutionalization, corpus salience, public-facing recognizability, and employment count. Employment count alone is a weak inverse proxy for niche/specialization.

### Unknown

- Whether training-corpus frequency, web-document frequency, or user-query frequency relate to persona geometry. OEWS employment counts do not measure any of those quantities.

## Strongest Correlations

The table below ranks the largest absolute Pearson correlations found in the sensitivity analyses. These are descriptive diagnostics, not claims.

| scope | model | predictor | target | n | pearson_r | spearman_r |
| --- | --- | --- | --- | --- | --- | --- |
| exact_close | qwen | log_annual_median_wage | pc2 | 26 | -0.614 | -0.605 |
| exact_close | llama | log_employment_count | pc1 | 34 | 0.588 | 0.679 |
| exact_close | llama | log_annual_median_wage | pc3 | 26 | 0.587 | 0.591 |
| exact_close_broad | llama | log_employment_count | pc1 | 50 | 0.584 | 0.694 |
| exact_close_broad | qwen | log_annual_median_wage | pc2 | 40 | -0.572 | -0.597 |
| exact_close_broad | qwen | log_annual_median_wage | pc1 | 40 | 0.565 | 0.628 |
| exact_close | qwen | annual_median_wage | pc2 | 26 | -0.555 | -0.605 |
| exact_close | gemma | log_annual_median_wage | pc2 | 26 | -0.544 | -0.540 |
| exact_close_broad | llama | log_annual_median_wage | pc3 | 40 | 0.543 | 0.584 |
| exact_close | gemma | log_annual_median_wage | pc3 | 26 | 0.534 | 0.517 |

## Sensitivity Notes

- Exact+close sensitivity uses only roles where the SOC mapping is direct or reasonably close.
- Broad sensitivity adds rough occupational-family proxies and should be read with lower confidence.
- Ambiguous mappings are preserved in `role_occupation_mapping.csv` but excluded from quantitative correlations.

## Cluster Summary

See `occupation_population_cluster_summary.csv` for matched-role employment and wage summaries by Qwen reference cluster. Small cluster counts make these summaries descriptive only.

## Interpretation Constraints

- Do not claim persona geometry reflects U.S. labor demographics.
- Do not treat OEWS employment count as training-corpus frequency.
- Do not force occupational mappings for archetypes.
- Wage is analyzed separately and is not treated as status.
- This tests only whether real-world professional prevalence has any detectable relationship to persona geometry among matchable occupational roles.

## Recommendation

This should remain exploratory follow-on work. It is probably future-work / appendix material, not Paper 1.5 core evidence. A stronger version would use occupational text/corpus frequency, O*NET descriptors, and a pre-registered mapping rubric rather than employment count alone.
