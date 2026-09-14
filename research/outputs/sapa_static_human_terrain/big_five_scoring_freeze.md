# SAPA Big Five Scoring Freeze

Status: PRE-TERRAIN SOURCE FREEZE

Date: 2026-09-13

The primary Stage 1 human coordinate system is the five administered IPIP100 Big Five domain scales recorded in the canonical SAPA scale inventory. This choice is frozen before any static-terrain calculation and is independent of model geometry.

The five domains are Agreeableness `IPIP100:B5:A`, Conscientiousness `IPIP100:B5:C`, Extraversion `IPIP100:B5:E`, Emotional Stability `IPIP100:B5:ES`, and Openness `IPIP100:B5:O`. Emotional Stability is retained in its native positive orientation for scoring and can be sign-reversed to Neuroticism only as a labeled display transformation.

Agreeableness uses 20 items: `q_140`, `q_146`, `q_150`, `q_195`, `q_200`, `q_217`, `q_838`, `q_844`, `q_1041`, `q_1053`, `q_1162`, `q_1163`, `q_1206`, `q_1364`, `q_1385`, `q_1419`, `q_1705`, `q_1763`, `q_1792`, `q_1832`.

Conscientiousness uses 20 items: `q_76`, `q_124`, `q_530`, `q_619`, `q_626`, `q_904`, `q_931`, `q_962`, `q_1254`, `q_1255`, `q_1290`, `q_1333`, `q_1374`, `q_1397`, `q_1422`, `q_1452`, `q_1483`, `q_1507`, `q_1696`, `q_1949`.

Extraversion uses 20 items: `q_55`, `q_241`, `q_254`, `q_262`, `q_403`, `q_690`, `q_698`, `q_712`, `q_815`, `q_819`, `q_901`, `q_1114`, `q_1180`, `q_1205`, `q_1410`, `q_1480`, `q_1742`, `q_1768`, `q_1803`, `q_1913`.

Emotional Stability uses 20 items: `q_108`, `q_177`, `q_248`, `q_497`, `q_890`, `q_952`, `q_960`, `q_974`, `q_979`, `q_986`, `q_995`, `q_1020`, `q_1099`, `q_1479`, `q_1505`, `q_1585`, `q_1677`, `q_1683`, `q_1775`, `q_1989`.

Openness uses 20 items: `q_128`, `q_132`, `q_194`, `q_240`, `q_316`, `q_422`, `q_492`, `q_493`, `q_609`, `q_1050`, `q_1058`, `q_1083`, `q_1088`, `q_1090`, `q_1388`, `q_1392`, `q_1738`, `q_1861`, `q_1893`, `q_1964`.

The exact scoring direction for each item is not manually reconstructed from item wording. It must be read mechanically from the canonical SAPA item dictionary fields `derived_scoring_keys` and `reverse_keyed_in_derived_scales`, using the derived keys `IPIP100agree`, `IPIP100consc`, `IPIP100extra`, `IPIP100stability`, and `IPIP100open` as present in the source dictionary. This prevents transcription or semantic-guessing errors.

No item outside these five frozen IPIP100 domains may enter the primary Big Five score simply because it improves later terrain structure. Alternate official representations, including BFAS aspects or SPI-derived five-factor scores, are sensitivity analyses only and must be labeled as such.

The scoring estimator itself remains subject to the preregistered missingness-recovery comparison in `analysis_specification.md`. This file freezes the construct source and item membership, not the winner of the respondent-scoring estimator comparison.

Source artifacts: `research/outputs/human_trait_dataset_feasibility/sapa/sapa_scale_inventory.csv` and `research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv`.
