# Broad SAPA PCA with frozen wellbeing overlay

CPU-only AA-13 analysis. Run:

```bash
python3 run_broad_sapa_pca.py --data-dir /authorized/path/to/doi_10.7910_DVN_SD7SVE
```

The raw SAPA matrix is an external, gitignored dependency. PCA is estimated without wellbeing; frozen HiFWB and Big Five scores are overlaid afterward. BFAS alignment is unavailable because no frozen respondent-level BFAS scoring definition was verified. See `analysis_freeze.md`, `source_manifest.json`, and `broad_sapa_pca_wellbeing_report.md`.
