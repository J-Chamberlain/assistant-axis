# Occupation-Prevalence Geometry Overlay

## Overview

This visualization is a descriptive follow-up to the occupation-population join. It overlays exact and close occupation-matched persona roles on Qwen PC1×PC2 geometry, with highlighted point size reflecting log U.S. occupational employment count where BLS OEWS values were available.

This is not a broad predictive claim. It is an inspection layer for seeing where common matched occupations sit in persona space.

## Data Coverage

- Geometry source: `research/geometry_tables/qwen_role_pc_rankings.csv`.
- Occupation source inherited from prior audit: BLS OEWS May 2025 national cross-industry estimates via `research/outputs/occupation_population_persona_join/`.
- Role mapping source: `research/outputs/occupation_population_persona_join/role_occupation_mapping.csv`.
- Total roles in background geometry: 275
- Exact matches: 47
- Close matches: 26
- Broad matches available only in optional view: 25
- Ambiguous mappings excluded from overlay: 25
- Unmatched roles excluded from highlighted overlay: 152
- Exact+close highlighted roles: 73
- Exact+close roles with employment counts: 34
- Exact+close roles with annual median wage: 27

## Visual Observations

### Observed

- High-employment exact/close roles are not spread uniformly across the map. The largest returned employment counts include `caregiver`, `secretary`, `accountant`/`auditor`, `recruiter`, `consultant`, and `lawyer`.
- Common service/administrative occupations such as `caregiver` and `secretary` sit closer to grounded-social or assistant-adjacent/procedural territory than mythic or trickster territory.
- Highly differentiated professional roles such as `accountant`, `auditor`, `lawyer`, and `consultant` appear on the high-PC1/procedural side, but the overlay also contains creative/media occupations outside that region.
- The exact+close overlay is visibly cluster-skewed because the role inventory contains many professional and media roles but many nonmodern/archetypal roles are intentionally unmatched.

### Inferred

- Weak global correlations can coexist with visually interesting regional concentration: the prior correlation table asks whether employment count tracks PCs linearly, while this overlay shows where a filtered subset of occupational roles lands in the geometry.
- The descriptive pattern is more useful as a coverage and territory-inspection tool than as evidence for a labor-demographic explanation of persona geometry.

### Speculative

- A stronger future analysis might compare OEWS employment counts with web-text frequency, O*NET descriptors, credentialing level, public-contact level, and institutional procedure intensity.

### Unknown

- Whether occupational employment count approximates role salience in model pretraining, user-query frequency, or prompt artifact frequency. This overlay does not measure any of those.

## Top Employment Exact/Close Roles

      role                                                        matched_occupation_title soc_code match_class  employment_count  annual_median_wage                 cluster       pc1        pc2
 caregiver                                             Home Health and Personal Care Aides  31-1120       close         4305810.0             35800.0         grounded_social  1.344612  14.616834
 secretary Secretaries and Administrative Assistants, Except Legal, Medical, and Executive  43-6014       exact         1706790.0                 NaN               editorial 40.755814  -3.400106
accountant                                                        Accountants and Auditors  13-2011       exact         1449500.0             83680.0               editorial 42.247903  -4.026883
   auditor                                                        Accountants and Auditors  13-2011       exact         1449500.0             83680.0 procedural_professional 48.155016 -12.294599
 recruiter                                                     Human Resources Specialists  13-1071       close          912430.0             75940.0 procedural_professional 32.779988   7.866917
  marketer                              Market Research Analysts and Marketing Specialists  13-1161       close          899580.0             78760.0 procedural_professional 34.081018   6.431733
consultant                                                             Management Analysts  13-1111       close          898280.0            101860.0 procedural_professional 41.026614  -2.691101
    lawyer                                                                         Lawyers  23-1011       exact          754500.0            159670.0 procedural_professional 42.993478 -11.861488
   trainer                                            Training and Development Specialists  13-1151       close          458300.0             69280.0 procedural_professional 33.863297   5.128512
 scheduler                                     Production, Planning, and Expediting Clerks  43-5061       close          390160.0             59650.0 procedural_professional 37.321814   2.676389
pharmacist                                                                     Pharmacists  29-1051       exact          321970.0            140910.0               editorial 37.875919  -4.241319
     coach                                                              Coaches and Scouts  27-2022       exact          248950.0             47320.0 procedural_professional 24.853860  11.699204

## Cluster-Level Summary

                cluster  exact_close_roles  roles_with_employment  total_employment_count  median_employment_count  median_annual_wage  median_pc1  median_pc2
procedural_professional                 50                     26               7356490.0                  99165.0             76345.0   30.217103   -3.011882
        grounded_social                 11                      3               4363230.0                  36180.0             41570.0   -8.988149   12.232802
              editorial                  9                      4               3626320.0                 885735.0             83680.0   35.130551   -2.114740
   combative_iconoclast                  1                      1                190650.0                 190650.0                 NaN   -2.564236   14.293777
       mythic_spiritual                  1                      0                     0.0                      NaN                 NaN  -59.201425  -14.699961

## Answer to Prompted Questions

1. Common matched occupations sit mainly in grounded-social, procedural-professional, and editorial/assistant-adjacent territories, with creative/media roles forming a visible secondary spread.
2. High-employment occupations visually concentrate more in grounded-social and procedural/administrative regions than in mythic/spiritual or trickster regions, but missing BLS values limit the claim.
3. Differentiated professional roles are overrepresented in high-PC1 procedural territory, especially accounting/auditing, law, consulting, and administrative/professional roles.
4. Common lower-degree or service occupations are underrepresented in the role inventory relative to the U.S. labor market, but available examples such as caregiver/secretary/bartender/paramedic tend toward grounded-social or service-adjacent regions when present.
5. The visual pattern differs from the weak global correlation result because the overlay emphasizes regional concentration of a filtered subset rather than linear PC-wide prediction.
6. The useful future-work question is whether occupational institutionalization, credentialing, public-contact intensity, or text/corpus frequency explains more than employment count alone.

## Caveats

- Do not claim persona geometry reflects U.S. labor demographics.
- Do not treat BLS employment count as training-corpus frequency.
- Do not infer prevalence for unmatched archetypal roles.
- Ambiguous and unmatched roles are excluded from the primary overlay.
- This belongs outside Paper 1.5 core evidence; at most it is a future-work note or appendix visualization.
