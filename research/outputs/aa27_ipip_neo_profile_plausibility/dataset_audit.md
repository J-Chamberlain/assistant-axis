# AA-27 source and density audit

**Dense-reference gate passes.** Johnson's first-party repository supplies 307,313 respondents ×300 item responses. There are 145,388 fully complete 30-facet profiles across all ages, including **117,260 adults aged 18–80** under the primary frozen rule. Allowing 9/10 items on every facet admits 294,985 across all ages and 237,832 adults. These are completeness eligibility counts before any hypothetical deduplication/splitting; no reference model or profile comparison was fitted because the semantic bridge fails.

## Source and reproduction

Primary repository: https://osf.io/tbmh5/ . Dataset component: https://osf.io/wxvth/ . Scoring component: https://osf.io/ycvdk/ . The browser fetch returned403, but the official OSF JSON API and its file-download URLs succeeded. No mirror or substituted dataset was used. Exact UTC retrieval times, filenames, URLs, byte counts and SHA256 are in `source_manifest.json`; download hashes match the OSF-provided hashes. Data selected are the 300-item file from the Johnson(2014) component, not its 120-item file or the separate 20,993-case 2005 component.

- `IPIP300.dat`,102,949,853 bytes, SHA256 `1bbb7189f5f0f2883bb4493f956cf639178c5c8ee95319fd3881f6d9d2f189a3`.
- `DAT300.doc`,54,272 bytes, SHA256 `b72ea04065dbc98c70ac69a6aa5bc58dd8896dcd33902b8d44930c58351cdb96`.
- `IPIP-NEO-ItemKey.xls`,54,784 bytes, SHA256 `d3f962e46b412151a2df571ebb5902bc0967c864ec5e05ab0a46d254dc0b52a0` (acquired source record).
- `IPIP-NEO-300 scoring tool_2.xlsx`,70,757 bytes, SHA256 `fe6365561c8f812fa2ddf305efe24f10e190ba7b8a168f48def5112753a31aff` (Input sheet used).

Official item wording and signs were independently matched against https://ipip.ori.org/newNEOFacetsKey.htm . All 300 facet assignments/signs agree, with three explicitly normalized minor wording variants at items 58/78/202. There are 148 negative-keyed items, ten items per facet, and thirty facets. The public worksheet's population norms were not used. The original key workbook was acquired and hashed; extraction used the newer coauthored300-item scoring workbook's Input sheet and the independent official IPIP web key.

## Scoring detail that prevents double reversal

DAT300.doc states that negative-keyed items were already recoded during inventory completion. Thus the downloaded1–5 values are already oriented; **apply no second6−x reversal**. Zero means missing. A complete facet's score would be its ten oriented items' mean; the alternative averages at least nine observed items. The independent key audit verifies the original direction and synthetic/raw-category reverse roundtrip. The density audit calculates observation counts, not human facet distributions. A mistaken second reversal would invert 148 items.

The 2018 documentation correction removed two leading blank columns from the data. The acquired version has 333 content bytes per record, with item 1 at one-based column 34 and item 300 at 333; the independent parser validates every line. CASE/time fields are not retained in outputs.

## Coverage and demographics

Overall item missingness: **0.403%**. Across respondents, missing-item median 1,90th percentile 3,99th percentile 8, maximum 10. Item-specific missingness ranges from0.109% to0.765%. `item_missingness.csv` reports all 300 items; `respondent_missingness_distribution.csv` is a histogram, not respondent rows; `human_facet_eligibility.csv` reports coverage per facet.

Complete-adult reported sex counts: female: 67,723; male: 49,537. Sex codes 1/2 are documented as male/female. Age bands and reported country codes are summarized in `demographic_summary.csv`. Most frequent complete-adult country-code groups: USA: 79,729; CANADA: 8,163; UK: 6,039; AUSTRALIA: 4,083; OTHER_SMALL_CELLS_OR_BLANK: 3,177. Blank and small country cells below 100 are aggregated, not individually exposed. Country codes are retained as reported, without inventing a nationality recoding. No representativeness claim follows from these counts.

This is a self-selected internet reference sample described in Johnson's repository, not a representative population sample. The freeze uses completion and age, with no post hoc removal based on unusual profile content and no claim to reproduce published quality-filtered norm samples. Possible careless responses, repeat participants, nonindependence and demographic selection would limit any later comparison. The contemplated split would deduplicate exact item patterns first, but was **not executed** after the semantic gate failure.

## Reuse and privacy

The official IPIP permission page (https://ipip.ori.org/newPermission.htm) places the items/scales/inventories in the public domain. The OSF parent and dataset node are public and explicitly make the data available for the cited research; their `node_license` fields are null. No separate dataset license was found in retrieved metadata/documentation. **Item public-domain status is not represented as an explicit dataset license.** Raw data and source workbooks stay in gitignored `data_external/aa27_ipip_neo/`; no human rows, CASE IDs, human profile vectors or nearest-neighbor records are committed. All analysis is local CPU.
