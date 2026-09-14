# Longitudinal Trait-Field Validation — Dataset Selection Freeze

Status: frozen before downloading or inspecting participant-level longitudinal outcome data.

## Objective

The next research question is whether a cross-sectional human trait field predicts the direction of actual within-person personality change. The central test is prospective and directional: given a person's observed Big Five displacement over time, does an independently frozen human trait field predict which narrower traits change, and in what direction, better than matched null or permuted predictions?

This analysis is distinct from the earlier static SAPA result. The SAPA field establishes conditional cross-sectional structure. The longitudinal study tests whether that structure forecasts real before/after change. A positive result would support predictive correspondence between static human trait geometry and observed change, not causal sequencing, intervention leverage, or a dynamical attractor model.

## Primary dataset choice

The primary candidate is the PEACH digital personality-change trial reported by Stieger et al. (2021), PNAS, DOI `10.1073/pnas.2017548118`.

Selection is frozen for methodological reasons established from public documentation before inspecting participant-level data. The trial enrolled 1,523 adults in a three-month digital coaching intervention targeting self-selected Big Five change goals. Self-reported personality was measured with the 60-item BFI-2 at pretest, posttest, and three-month follow-up, with additional observer reports using the BFI-2-S. Public reports indicate 554 participants completed posttest and 437 completed the three-month follow-up. The dataset is deposited on OSF under the source project cited by the original paper.

A secondary intensive-longitudinal source from the same intervention is the weekly process dataset analyzed by Allemand et al. (2024), European Journal of Personality, DOI `10.1177/08902070231225803`. It contains weekly BFI-2-S personality-state measurements over 11 weeks for participants primarily targeting Emotional Stability, Conscientiousness, or Extraversion. This source is secondary because the weekly instrument is shorter and the published process sample is restricted to the three largest change-goal groups.

The facet/nuance analysis by Olaru et al. (2024), DOI `10.1177/08902070221145088`, confirms that the PEACH outcome dataset contains repeated item-level BFI-2 self-report data sufficient to distinguish domain, facet, and item-level change. It also documents substantial heterogeneity in lower-level change, which is necessary for the proposed prediction test.

## Why this dataset is preferred

The trial contains actual intentional personality change rather than passive long-interval drift, repeated broad and narrow personality measurement, an intervention that produces heterogeneous participant-level change vectors, pre/post and follow-up measurements, and observer reports for a methodologically distinct sensitivity analysis. It therefore matches the research question more closely than large panel studies that repeat only short Big Five domain measures.

The PEACH sample is not population-representative and has substantial attrition. Those limitations affect generalization and selection but do not invalidate a within-person directional prediction test. Attrition and change-goal composition must be reported explicitly and handled in sensitivity analyses.

## Compatibility decision

The existing SAPA 12-trait field remains the primary human/model bridge object and will not be retuned using PEACH outcomes. However, the BFI-2 does not directly measure all 12 bridge traits. Forcing an outcome crosswalk after viewing longitudinal change would create avoidable researcher degrees of freedom.

Therefore the primary longitudinal validation will test the more general geometric claim using a separately frozen BFI-2-compatible lower-level field. Before PEACH outcomes are inspected, a human-only BFI-2-compatible field will be constructed from SAPA using externally defined BFI-2 facet semantics and available SAPA item/scale evidence. The target representation will be the 15 BFI-2 facets where defensible human-side measurement can be formed without using PEACH outcome data. The exact retained facet set and scoring rules must be frozen before the participant-level PEACH file is opened.

The existing 12-trait SAPA field remains a secondary bridge-specific object. If a subset of the 12 traits has a defensible pre-outcome BFI-2 proxy based only on published item/facet definitions, that subset may be evaluated as a separately frozen secondary analysis. No trait will be added, removed, or remapped based on longitudinal performance.

## Independence requirements

The SAPA field and any BFI-2-compatible SAPA facet field must be finalized without PEACH participant-level outcome data. Dataset selection uses only public study documentation. Model geometry, activation vectors, persona labels, model trait scores, and model-side performance do not enter the human longitudinal validation.

## Deferred access issue

The public OSF pages are not directly retrievable in the current browser environment because OSF returns access/robot restrictions to this runtime. This is an access constraint, not a scientific blocker. The analysis design and human-side compatible field can be frozen first. If automated retrieval remains blocked after the freeze, the participant-level OSF file can be downloaded manually and uploaded to the active analysis environment without changing the preregistered design.
