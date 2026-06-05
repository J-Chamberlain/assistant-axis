# Data Source Manifest

## Official Source

- Dataset: Bureau of Labor Statistics Occupational Employment and Wage Statistics (OEWS), national cross-industry estimates.
- Vintage/year used: May 2025; API query year `2025`.
- OEWS tables page: https://www.bls.gov/oes/tables.htm
- OEWS time-series documentation: https://download.bls.gov/pub/time.series/oe/oe.txt
- OEWS datatype definitions: https://download.bls.gov/pub/time.series/oe/oe.datatype
- BLS public API endpoint: https://api.bls.gov/publicAPI/v2/timeseries/data/

## Field Definitions Used

- `employment_count`: OEWS datatype `01`, employment estimate. BLS documentation states employment estimates are rounded to the nearest ten and self-employed workers are not included.
- `annual_mean_wage`: OEWS datatype `04`.
- `hourly_median_wage`: OEWS datatype `08`.
- `annual_median_wage`: OEWS datatype `13`.
- Series construction: `OE` + seasonal `U` + area type `N` + area `0000000` + industry `000000` + six-digit SOC occupation code + datatype code.

## Local Download/Query Path

- Full BLS bulk downloads were not stored because direct scripted access to the BLS ZIP/text download hosts returned HTTP 403 in this environment.
- The helper script queries only the needed official BLS public API series and writes the normalized outputs in this directory.
- Role-to-SOC mappings are manual, conservative, and auditable in `role_occupation_mapping.csv`.

## Core Geometry Sources

- Qwen canonical role table: `research/geometry_tables/qwen_role_pc_rankings.csv`
- Cluster membership table: `research/geometry_tables/cluster_membership_table.csv`
- Multi-model coordinate table: `research/outputs/cross_model_cluster_topology/per_model_cluster_assignments.csv`
