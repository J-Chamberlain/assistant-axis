# Frozen Qwen-PC → human-construct match rubric

Rubric version: 1.0  
Frozen before any PC candidate was assigned a final status: 2026-09-12T08:25:00Z  
Analysis model: GPT-5.5  
Discovery model: Qwen/Qwen3-32B only

## Scientific object

This rubric evaluates whether an established human psychological construct is a useful *discovery description* of a broad Qwen role-vector principal-component pattern. It does not test whether the same latent variable exists in humans and Qwen, and it does not authorize respondent-level projection.

Domain, aspect, facet, and narrow-trait candidates are evaluated at their stated level. A domain is not penalized merely because it overlaps its aspects or facets. Hierarchical overlap must instead be reported explicitly.

## Evidence dimensions

Every candidate row preserves these dimensions separately:

1. **Model-trait profile coverage:** coverage of the full positive and negative Qwen trait pattern, not label resemblance to one trait.
2. **Role-profile coverage:** coverage of the top and bottom role distributions and important counterexamples.
3. **Existing blinded interpretation evidence:** agreement or tension with coordinate-blind prompt-dossier interpretations already completed for PC1-PC3. PC4-PC6 have no equivalent mature blinded interpretation and this absence counts as a limitation.
4. **Human construct definition and item content:** fit to an authoritative construct definition and to the actual public-domain SAPA item content.
5. **Human measurement quality:** SAPA item availability, released scoring key, pairwise-complete reliability diagnostic, and planned-missingness implications.
6. **Focused activation evidence, where available:** recorded separately and never treated as human evidence. At freeze time this exists only for PC1 accountability contrasts.

Each dimension receives one of `SUPPORTS`, `PARTIAL`, `CONTRADICTS`, or `UNAVAILABLE`, plus a short auditable rationale. No opaque weighted score is calculated.

## Match statuses

### STRONG CANDIDATE

Use when the construct, at its declared hierarchical level, covers both poles or the major contrast of the PC across model traits and roles; at least four of the first five evidence dimensions support the match; no major human-definition contradiction is present; and a reproducible human measure of the construct is available. Focused activation evidence may strengthen but is never required. For PC4-PC6, lower axis stability and the absence of a mature blinded interpretation must be stated even if this status is assigned.

### PLAUSIBLE PARTIAL CANDIDATE

Use when multiple evidence classes support a real component of the PC but the construct misses a substantial residual, fits only one pole, conflicts with important role or trait evidence, or has limited measurement quality. This is the default for plausible mappings to supported secondary axes when evidence is incomplete.

### FACET / SUBCOMPONENT

Use when the construct is a defensible lower-level part of a broader candidate but is too narrow to describe the complete PC. A facet may coexist with its parent domain; this is hierarchy, not a contest.

### BROAD BUT NONSPECIFIC

Use when a broad construct correlates with or loosely describes the PC but cannot distinguish the focal pattern from several materially different alternatives. Broadness alone is not disqualifying; lack of specificity to the observed signature is.

### POOR MATCH

Use when the authoritative construct definition or item content materially conflicts with the Qwen trait/role pattern, or when apparent support is primarily lexical resemblance without multi-evidence coverage.

### INSUFFICIENT EVIDENCE

Use when the axis is too weak/unstable, the candidate lacks adequate definition or measurement, or the available evidence cannot adjudicate the mapping. `NO DEFENSIBLE HUMAN CONSTRUCT IDENTIFIED` is permitted at the PC level.

## Selection procedure

1. Examine the complete frozen Qwen signature for one PC, including all 240 trait associations, 40 role extremes, cluster distribution, stability, Qwen-only strict Big Five associations, and prior Qwen-only evidence.
2. Generate candidates from the complete 92-construct human library. The former 78 literal trait links are not the candidate universe.
3. Complete PC1 as the worked example using the dimensions above.
4. Keep this rubric unchanged and apply it to PC2-PC6.
5. Preserve all serious alternatives and mismatches. Do not force a single construct or exclusive assignment.
6. Freeze final candidate rows before writing the held-out validation plan.

## Firewalls

- No AA-7 result is an input.
- No Llama or Gemma value is an input to candidate generation, status assignment, or freezing.
- No human respondent is scored or projected into Qwen space.
- No construct is selected because it improves PC prediction.
- Model-side associations are same-space discovery evidence, not independent psychological validation.

The final validation status for every retained hypothesis must be `DISCOVERY_ONLY / NOT YET CROSS-MODEL VALIDATED`.
