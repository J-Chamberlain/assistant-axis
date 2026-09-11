# SAPA Category-3 Blinded Second-Pass Review Rubric

Version: `1.0`

Frozen: `2026-09-11`

Review type: coordinate-blind second-pass semantic review

## Review question

Given only the canonical model-trait construct definition and the supplied SAPA item/scale evidence, is the proposed correspondence sufficiently direct to retain in a later human/model trait bridge?

This rubric evaluates semantic and measurement correspondence only. It is not independent psychometric validation. The reviewer must not consult persona identities, PC coordinates, trait-PC correlations, prediction coefficients, sparsity results, occupation or NLSY97 outcomes, downstream correspondence results, or any other measure of a trait's usefulness for model geometry.

## Allowed evidence

- Canonical model-trait name and definition/prompt.
- Candidate SAPA item IDs and exact item wording.
- SAPA source-scale membership and the limited primary scale metadata included in the packet.
- SAPA item response anchors and documented reverse-key metadata when present.

The SAPA release does not supply prose construct definitions in the committed scale inventory. A scale label or membership may support a judgment, but must not substitute for the exact item wording.

## Decisions

### ACCEPT_DIRECT

Use when the retained SAPA evidence measures essentially the same narrow construct as the canonical model trait. Ordinary wording, perspective, or setting differences are acceptable only when they do not change the construct boundary. A single highly face-valid item may qualify, but its single-item status must remain explicit.

### ACCEPT_CLOSE

Use when the evidence measures a clearly related narrow construct suitable for a separately flagged secondary bridge tier, but is not sufficiently identical for direct status. Typical reasons include a modest behavior-versus-style distinction, narrower or broader scope, or partial coverage of a multi-part canonical definition.

### DOWNGRADE_BROAD

Use when the evidence supports only a broad parent domain, such as general Agreeableness, Openness, Extraversion, conscientiousness, or emotional stability, rather than the named narrow construct.

### REJECT

Use when the proposed correspondence is weak, substantially different, context-specific in an incompatible way, dependent on an unjustified inference, or contradicted by the supplied wording.

### AMBIGUOUS

Use when the supplied evidence is insufficient or internally mixed such that a clean semantic adjudication is not warranted.

## Required fields for every judgment

- `decision`: exactly one of the five values above.
- `rationale`: a brief item-grounded explanation.
- `evidence_item_ids`: the primary supplied item IDs used in the judgment.
- `evidence_scale_names`: the relevant supplied SAPA source-scale IDs/names.
- `single_or_multi_item`: `single_item` or `multi_item`.
- `reverse_direction_issue`: `none`, `handled`, or `unresolved`, with any detail in the rationale or construct-boundary note.
- `construct_boundary_note`: the narrowest important mismatch, or `none`.

## Adjudication rules

1. Judge every row from the frozen packet only.
2. Do not infer missing psychological definitions from a scale abbreviation.
3. Give exact item wording precedence over a scale label.
4. Do not preserve a mapping because it was previously placed in Category 3.
5. Do not reward scientific convenience, likely downstream predictiveness, or coverage retention.
6. Treat direct and close tiers as distinct in every summary and downstream file.
7. If reverse wording is usable, document how direction must be reversed; if direction cannot be resolved, use `AMBIGUOUS` or `REJECT` as appropriate.
8. Do not change this rubric after aggregate results are viewed. Any revision requires a new version and a complete rerun.

## Interpretation boundary

An accepted row is a provisional content correspondence. It does not establish scale validity, measurement invariance, respondent-level score comparability, causal equivalence, or correspondence between human distributions and Qwen representations.
