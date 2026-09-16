# LISS data-access handoff

LISS respondent-data access is pending. Do not bypass Centerdata controls. Each user must sign the LISS statement and download authorized files directly.

Place these exact files under gitignored `data_external/liss_2020/`:

- `cp20l_EN_1.0p.dta` and `codebook_cp20l_EN_1.1.pdf` — Study 965: https://www.dataarchive.lissdata.nl/study-units/view/965
- `ss20a_EN_1.0p.dta` and `codebook_ss20a_EN_1.0.pdf` — Study 1105: https://www.dataarchive.lissdata.nl/study-units/view/1105

Use `nomem_encr` for the local authorized join. Run `verify_liss_2020_sources.py` to record SHA256 values only after files arrive, then validate schema. Raw microdata and identifiers stay local and gitignored; do not commit, upload, share, or redistribute them. If Centerdata terms restrict use with external AI systems, preserve that restriction and keep all respondent-level execution local. Only aggregate, disclosure-reviewed outputs may enter version control.
