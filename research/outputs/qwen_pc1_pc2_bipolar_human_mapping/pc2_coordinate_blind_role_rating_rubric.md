# PC2 Coordinate-Blind Role-Rating Rubric

Status: frozen before any rating-to-geometry join

Rater: GPT-5.5 / Codex analytical workflow

## Blindness boundary

The rating builder may read only `role` and `positive_instruction_1` through `positive_instruction_5` from the canonical 275-role inventory. It must not read PC coordinates, PC ranks, percentiles, clusters, existing interpretations, trait correlations, or specificity classifications. The builder enforces this by selecting allowed columns immediately after CSV parsing and by rejecting any output column containing `pc`, `rank`, `percentile`, `cluster`, `correlation`, `specificity`, or `purity`.

## General coding rule

Rate what the instructions make central to performing the role, not what a person with that job might incidentally do. Repeated template wording does not by itself justify a high score. Dimensions are independent: a role can score high on both physical and conceptual engagement, or on both practical action and formal mediation.

The frozen implementation uses explicit phrase families and capped frequency counts over the role name plus all five instructions. Phrase families were written from the definitions below before geometry was inspected. They are transparent proxies for a reading-based semantic judgment and should not be described as human ratings or independent validation.

## Shared ordinal anchors

- `1` — absent or contrary: the role does not center the dimension.
- `2` — peripheral: the dimension is plausible but not a recurring or defining demand.
- `3` — meaningful: the dimension is an explicit recurring part of the role.
- `4` — central: the role substantially depends on the dimension across instructions.
- `5` — defining: the dimension is indispensable to the role as instructed.

## Dimension definitions

### EMBODIED_PHYSICAL_ENGAGEMENT

Bodily movement, direct physical action, manual skill, sensory engagement, sport, combat, field activity, or active participation in a physical environment. References to physical phenomena or bodies in an abstract explanatory role do not suffice.

### PRACTICAL_CONCRETE_ENGAGEMENT

Real-world application, implementation, repair, operations, direct problem solving, concrete action, or producing an observable result. Planning or analysis alone is insufficient unless instructions connect it to implementation.

### SOCIAL_OUTWARD_ENGAGEMENT

Interpersonal interaction, public participation, persuasion, coordination, care, teaching, performance, or engagement with groups. Merely answering a user is not scored as social centrality.

### ABSTRACT_CONCEPTUAL_ENGAGEMENT

Theories, concepts, symbolic reasoning, scholarship, synthesis, world models, interpretation, or sustained reflection on underlying principles. Technical work can score highly when conceptual modeling is central.

### RITUAL_FORMAL_MEDIATION

Formalized, ceremonial, rule-bound, protocol-governed, contemplative, traditional, or symbolically mediated engagement. This deliberately covers two related but distinguishable forms named in the hypothesis: institutional procedure and ritual/contemplative mediation. The later report must inspect whether any association is driven by only one form.

## Interpretation limits

The scores are a deterministic coordinate-blind content coding of role instructions. They are not observed behavior, human judgment, questionnaire measurement, or an independently replicated semantic rating. Correlations are descriptive and cannot establish that PC2 is physicality, practicality, extraversion, or any other human construct.

