# Broad SAPA PCA with frozen wellbeing overlay

CPU-only AA-13 analysis. Run:

```bash
python3 run_broad_sapa_pca.py --data-dir /authorized/path/to/doi_10.7910_DVN_SD7SVE
```

The raw SAPA matrix is an external, gitignored dependency. PCA is estimated without wellbeing; frozen HiFWB and Big Five scores are overlaid afterward. Follow-up checks include 200-replication parallel analysis, 50 split-half fits, and 2,000 paired test bootstraps. The bounded conclusion is C (no reliable incremental structure) pending deferred repeated-split and residual/instrument-balanced refits. BFAS alignment is unavailable because no frozen respondent-level BFAS scoring definition was verified.
