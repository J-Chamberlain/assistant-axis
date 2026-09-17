# Existing trait bridge audit

Observed: The frozen 240-label AA-14 vocabulary was joined by exact trait label to the prior 240-row feasibility crosswalk and the retained provisional 74-row SAPA bridge (45 direct, 29 close). No new semantic remapping was performed. The bridge records exact SAPA item composition, wording, source scales, and prior psychometric-support tier; the complete 240-row audit is `existing_trait_bridge_audit.csv`. `sapa_proxy_construct` is the prior bridge's working trait-proxy name (not an official SAPA scale score); `sapa_source_scales` lists the actual item-source scales.

Absent labels (166) have no retained SAPA proxy. The original feasibility category is preserved for context but does not promote an absent label into a direct or close match. No ambiguous candidate was admitted to the primary profile.

Observed: 4 exact item-set groups involve 8 model labels; the secular/spiritual group is reverse-keyed rather than two independent human observations. Exact group IDs are SHA256 prefixes of sorted item IDs, and partial item/scale reuse is separately listed. The composite overlap exclusions are chill (q_820), confident (q_820), melancholic (q_1578), neurotic (q_1578), playful (q_1043). Overlap is tested against each outcome separately as well.

The primary composite profile uses only direct, nonoverlapping mappings; close mappings are retained as a sensitivity tier. Both tiers receive observed association values in the descriptive table, with mapping provenance and eligibility explicit. Multiple model labels tied to the same human item set must be collapsed or weighted in downstream inference. This Stage 1 makes no across-trait inferential test.

The AA-13 external-matrix schema fingerprint was transcribed as a 63-character string; recomputing SHA256 of the full 719-column header joined with ASCII unit separators gives `787f539747deee8da85bc64da9c3407eaf741f6da9277dcbec7ec79b2a40260c`. The raw-file SHA256 and 23,679 × 719 dimensions match the frozen dependency.
