# LISS 2020 measurement notes

Study 965 (Personality, May–June 2020) reports selected 6969, nonresponse 1046, response 5923, complete 5859. Expected data file: `cp20l_EN_1.0p.dta`; join key: `nomem_encr`; codebook: `codebook_cp20l_EN_1.1.pdf`. Blocks are cp20l010–011 happiness/satisfaction (0–10), cp20l012–013 mood (1–7), cp20l014–018 SWLS (1–7), cp20l020–069 BIG-V (1–5), cp20l070–079 Rosenberg (1–7), cp20l135 IOS (1–7), cp20l146–165 PANAS (1–7), and cp20l198–207 LOT-R (1–5).

Study 1105 (Social Science, May 2020) reports selected 3571, nonresponse 847, response 2724, complete 2719. Expected data file: `ss20a_EN_1.0p.dta`; join key `nomem_encr`; codebook `codebook_ss20a_EN_1.0.pdf`. `ss20a001` randomizes four versions: v1 `002–019` past week plus `020–025` past month; v2 `026–039` past month; v3 `040–053` past week; v4 `054–071` past month. Responses are 0–5 frequency categories. Preserve version/timeframe; do not pool without measurement checks.

The codebook PDF contains a `nomem_encr2` typo in one passage; the study join key and footnote use `nomem_encr`.
